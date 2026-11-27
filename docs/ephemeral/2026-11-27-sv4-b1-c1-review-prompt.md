# SV4 B1-C1 exact-head review prompt — the token's custody (a handle written first), with a written threat model

- **Owner:** App Manager 13. Nathan starts this session manually, in the `Glow App - No Stream` environment (OD-36), and relays its report.
- **Revision 1, 27 November 2026.**
- **Durable brief:** [SV4 — the chat and notifications slice](../planning/sv4-chat-notifications.md), revision 13: D18's custody bullet (DM-102's AN1), D24 (AN2), and "Review plan (Stage B)". **The decision:** [DM-102](../continuity/dev-manager/reviews/2026-11-27-dm-102-sv4-b1-c1-custody.md), whose section 5 sets this review's focus.
- **Where the result goes:** the report Nathan relays. The manager records it in the SV4 record, "Exact-head review of B1-C1", with a disposition for each finding (a correction before the merge, or carried), and in the brief's "Sessions".
- **Model and reasoning setting** (OD-10, OD-30, OD-33, OD-34, OD-42). The reading is the recommendation; it gates nothing, and Nathan picks.
  - **TypeSafe v8.2: Opus 5.5 at extra high.** Effort score 2.81 (confidence 0.84); rung probabilities low 0.00, medium 0.00, high 0.21, extra high 0.76, max 0.03, ultracode 0.00. Model probabilities Fable 5.1 0.14, Opus 5.5 0.86, Sonnet 5.5 0.00, Haiku 5.5 0.00 (confidence 0.81). Twenty-four cells, computed from the two answers: Fable 5.1 at low 0.000, Fable 5.1 at medium 0.000, Fable 5.1 at high 0.029, Fable 5.1 at extra high 0.106, Fable 5.1 at max 0.004, Fable 5.1 at ultracode 0.000, Opus 5.5 at low 0.000, Opus 5.5 at medium 0.000, Opus 5.5 at high 0.181, Opus 5.5 at extra high 0.654, Opus 5.5 at max 0.026, Opus 5.5 at ultracode 0.000, Sonnet 5.5 at low 0.000, Sonnet 5.5 at medium 0.000, Sonnet 5.5 at high 0.000, Sonnet 5.5 at extra high 0.000, Sonnet 5.5 at max 0.000, Sonnet 5.5 at ultracode 0.000, Haiku 5.5 at low 0.000, Haiku 5.5 at medium 0.000, Haiku 5.5 at high 0.000, Haiku 5.5 at extra high 0.000, Haiku 5.5 at max 0.000, Haiku 5.5 at ultracode 0.000. Sent 2026-11-27T05:12:08Z. Nathan picks the cell.
- **The Dev Manager's read:** none before it runs. The review authorizes no credential use and no live provider action. Dev Manager 7's pre-merge read of B1 follows this review (D-07).
- **Environment** (OD-36): `Glow App - No Stream`. No Stream variable is needed, and none may be present. `amthorn78/glow-docs` is attached, read only; this review needs nothing from it (OD-74).
- **It runs alone** (OD-29), after PR60's run and Codex's review of the manager-branch head that holds this prompt (manager workflow, step 6). A full exact-head review of B1-C1, not a delta review: B1-C1 changes D18's and D24's custody design (DM-102, item 4).
- **Deletion condition:** prune after B1's pull request (PR60) merges and its merge receipt is recorded.

**Manager:** before giving this prompt to Nathan, replace every `<PROMPT_SHA>` with the full SHA of the manager-branch commit that holds this revision.

---

You are the **exact-head review of SV4 B1-C1**, the correction of B1's token custody, for the Glow dating app, in the public repository `amthorn78/glow-dating-app` (public for now; OD-51). You review one exact code head in full, with a written threat model. This prompt is revision 1, from commit `<PROMPT_SHA>` of the manager branch `claude/magical-wozniak-yfmmx2`.

**What came before.**
- **B1** (code head `e7e7e84`; the SV4 record `docs/testing/evidence/2026-11-19-sv4-chat-notifications.md`, section "B1") built F12's surface: three sealed routes, the persistence port and its ORM adapter (`services/api/glow_notifications/persistence.py`), migration `0014` and twelve chat-suite cases. PR60 carries it into `main`, which is at `988a36a`.
- **B1's exact-head review** (the record's "Exact-head review of B1") found F12's behaviour right on every route, and found custody open:
  - **B1R-1** (Codex's P2, comment 4713760650): a handled database failure after the store's `put` lost the reference;
  - **B1R-2** (Codex's second P2, comment 4715163584): after a lost commit acknowledgement, a reference a registration holds was also parked, and the owner's later revoke was refused;
  - **B1R-3:** nothing failed when a retired reference was not held for its discard;
  - **B1R-4 to B1R-7:** words.
- **DM-102** (Dev Manager 7; the record's "Dev Manager 7's DM-102") chose form (b): the new reference's pending discard is written as its handle before the command's transaction, and the save consumes it. Its conditions are AN1 (now D18's custody bullet) and AN2 (D24's sweep rule, for B2), with words AN3 to AN11.
- **B1-C1** (branch `claude/funny-hypatia-lpzbn0`; the record's section "B1-C1"): code head `48f0801`, run of record 45941121120 (all twelve jobs; the chat suite 37/37), records head `1502359`. The manager verified it ("Manager verification of B1-C1") and merged it into the manager branch at `4185119`. The session recorded two judgments of its own:
  - the handle takes two statements, the conditional insert and a re-read of the registrations (`_held_since`), because under concurrency the insert's snapshot can miss a save;
  - four of B1's cases now find their reference by the store's issue order rather than by its token, since a discarded reference resolves to no token. The prompt had not allowed that change (AM13-18).

**The code head under review is `48f0801`.** You work at `<PROMPT_SHA>`, whose non-Markdown paths are byte-identical to `48f0801` (the start gate checks this). B1's own exact-head review certified `e7e7e84`; it does not certify this head.

**Your scope:**
- **The code:** `git diff f7a21b9ce69a24eff03015c1b1315d8d75e425e3 48f08017350993c13bccb78095e084ad0434a6a5`, B1-C1's code commit, its 13 paths (10 of them non-Markdown; `f7a21b9`'s non-Markdown paths equal `e7e7e84`'s), each changed module read whole at `48f0801`, beside its version at `e7e7e84`:
  - `services/api/glow_notifications/persistence.py` and `contract.py`;
  - `services/api/glow_domain/notifications.py` and `notification_fixtures.py`;
  - `services/api/glow_persistence/models.py`;
  - `services/api/tests/test_notifications_routes_offline.py` and `test_notifications_port.py`;
  - `proofs/postgres-ordering/glow_ordering_proof/chat_cases.py` and `chat_support.py`, and `proofs/postgres-ordering/tests/test_chat_offline.py`.
- **What B1-C1 relies on unchanged,** read where it relies on it: the rest of `persistence.py` (the locks, the transfer, the bound, idempotency, the read and the settings command); SV2's `glow_profiles/tx.py` and `idempotency.py`; migration `0014`'s `PendingTokenDiscard` and `DeviceRegistration` constraints; `chat_suite.py`.
- **The Markdown, as claims about the code:** `docs/architecture/production-contracts.md` and `data-model.md` (their changed lines), `proofs/postgres-ordering/README.md` (the chat suite's paragraph), and the record's sections "B1-C1" and "Manager verification of B1-C1", whole.
- **The runs:** 45941121120 (the run of record), and PR60's run on `<PROMPT_SHA>` (event `pull_request`), once it has finished; Codex's reviews of `<PROMPT_SHA>` and any thread on PR60.
- **Out of scope:** B2's sweep (it does not exist yet; you read the contract B1-C1 leaves it), the real token store (P09.2, P11B), and B1's surface outside custody, which B1's review read. Report only where B1-C1's change affects them.

**The threat model.** Write it in your report:
- **Assets:**
  - a device's push token, which no row, log line, answer, exception, receipt or results file may hold;
  - the token store's reference, held only by an active registration's row or a pending discard's row (AN1), and by no row only after a process stop, or a failed handle write and a failed discard, between the `put` and the handle;
  - a registration in use: its reference never discarded while an active registration holds it, and its owner's revoke, rotation or transfer never refused because the reference is also pending;
  - the pending discards as B2's sweep will read them (AN2): a row the sweep may take is one no registration holds and no running command can still save.
- **Actors:**
  - a member's register, rotate, revoke or transfer, alone and racing another command on the same account or installation;
  - two commands holding one reference, which only a store that breaks AN11 can produce;
  - the database refusing, failing or becoming unreachable at each statement: the handle's write, its re-read, inside the transaction's body, at the commit, and at each discard;
  - a commit that takes effect but whose answer is lost;
  - B2's sweep, removing a pending discard between a command's handle and its save;
  - the token store refusing, failing, or discarding a reference already discarded;
  - the CI runner, its logs and its artifacts.
- **Entry points:** `OrmNotificationPersistence.device()`, `_run`, `HANDLE_WRITE`, `_write_handle`, `_held_since`, `_consume_handle`, `_discard_unwritten` and `_discard`; `FixtureTokenStore.reuse_next_put`; the chat suite's simulations in `chat_support.py` (the execute wrapper, the shadowed commit, `BeginHold`).

For each threat, give the code that stops it and the test or run that proves it. **The focus** (DM-102, section 5, and the session's judgments):
1. **The handle's write and its condition.** `HANDLE_WRITE`'s `INSERT … SELECT … WHERE NOT EXISTS … ON CONFLICT … DO NOTHING RETURNING id`, in autocommit, after the `put` and before `_run`.
   - Say whether it writes a handle only for a reference no registration and no pending discard holds, and whether "no row returned" and "an error raised" tell a reference held from a failed write in every case, under concurrency as well as alone.
   - Say whether a reference already held is refused with nothing discarded and nothing written, and whether a failed write discards the reference at once.
   - **`_held_since`:** say whether the race it answers is real on PostgreSQL at READ COMMITTED, whether its re-read closes it, whether removing the handle by key and refusing is right, and whether a failure of the re-read leaves only what the record says. Say whether AN1's "written in its own statement" is met by the two statements, or the design departs from DM-102.
2. **The save's count check.** `_consume_handle` deletes the handle by key and reference inside `_register`, after the registrations' locks, and refuses `token_handle_missing` (`state_conflict`, not retryable) unless one row went.
   - Say whether a save and AN2's sweep can both win, whether a command slower than the sweep's bound can save a reference the sweep has discarded, and whether every save path consumes its handle: a first registration, a rotation, a re-registration and a transfer.
   - Say whether the delete's place in the lock order can deadlock against B1's other commands, chat's writers, or a sweep that removes a row in its own transaction.
3. **`_run`'s outcome split.** `returned` is set once the body returns: a failure before it is known, one after it (the `before_commit` hold point, the commit) unknown.
   - Say whether every failure that rolled back is known (a refusal, a deadlock, an `IntegrityError` inside the body, a failure at the transaction's start) and whether every failure that may have committed is unknown.
   - Say whether Django's `atomic` can raise after the body returns for a reason that did not reach the commit, and what follows if it does.
   - Say whether the read and the settings command answer as before.
4. **The immediate discards.** A known outcome that did not save discards the reference at once through `_discard`; a failed discard leaves its row.
   - Say whether any known path leaves a reference with no row, discards one a registration holds, or leaves a handle the sweep must take.
   - Say whether a replay, a refusal inside the locks, the bound, a stale version and a transfer that changed each take this path.
   - Say whether a double discard (a refusing command and the sweep) is harmless under AN11's rule.
5. **The unknown-outcome path.** The handle is left and nothing is discarded. Say whether, after a commit that took effect, the registration holds the reference and no pending row does, and the owner's later revoke, rotation or transfer is accepted (B1R-2's symptom gone). Say whether, after a commit that did not take effect, the handle is left for the sweep and nothing else holds the reference.
6. **D24's contract as B2 inherits it.** From the code and AN2: what a pending row means; when the sweep may take one (past its bound, no registration holding its reference); what it must do (remove the row in its own transaction, then discard, writing the row again if the discard fails); and the clock the bound reads (the handle's `created_at`, the application's). Say whether the carried entry for B2 (the carried-items file, B1-C1's entry) states every rule B2 needs, including how a row ends that a registration holds after a failed re-read.
7. **The cases and the simulations.** Check each of the seven new cases against B1-C1's prompt, section 3, item 8, and DM-102's section 4.
   - Say whether any is vacuous, and whether each fails under its reversal.
   - Say whether each simulation stands for what the record says, and what it cannot show: the execute wrapper failing the handle's write; the shadowed commit that runs and then raises; `BeginHold`.
   - Say whether any simulation is a switch inside the adapter (the adapter's docstring says there is none).
   - Say whether `notifications.no_token_in_any_row_or_answer` still checks every reference the store issued, the new cases' included.
8. **The earlier tests.** Each changed earlier test gains only what B1-C1's prompt, item 9, names, and the four cases' lookup.
   - Say whether the lookup by issue order finds the same reference the by-token lookup found, in every case and order the plan can run, and whether any other line of those cases changed.
   - Say whether the case count's pin and the plan tests gain only the seven cases, and whether the hidden-publishing cases still run last.
9. **The custody sentences.** Check each against AN1 and the code:
   - AN3 to AN7 in `production-contracts.md` and `data-model.md`;
   - AN11 in `TokenStore`'s docstring;
   - the adapter's module docstring and `PendingTokenDiscard`'s docstring;
   - B1R-7's sentence;
   - AN8's mark, and the record's section "B1-C1", whole, with "What B1-C1 changes in section B1".

   Say whether any claim a decision or the merge would read is false. The stale lines the manager routed to B2 (the codes bullet's two reasons; the README's line 76) are recorded: say whether either is a false claim D-07 names before the merge.
10. **Codex's two threads.** Say whether B1-C1's code answers each: comment 4713760650 (`_park`, a lost reference) and comment 4715163584 (an unknown commit outcome).
11. **The rest of B1 at this head.** Say whether `git diff e7e7e84 48f0801 -- . ':!*.md'` touches any path or passage outside custody and its tests. Say whether B1's review's findings outside custody (its threat model's other rows; B1R-8 and B1R-9, carried) still stand as B1's review found them.

**Re-run, at least,** in a scratch copy of `48f0801`, each package in a virtual environment installed from its own lock with `pip install --require-hashes`, under `env -i`:
- **The API:**
  - `GLOW_ENV=test python manage.py check && GLOW_ENV=test python manage.py test tests`;
  - `ruff check .`, `ruff format --check .` and `mypy`, and `mypy glow_notifications` by name, since CI's list does not name it;
  - `GLOW_ENV=test python manage.py makemigrations --check --dry-run`.
- **The ordering proof:** its offline tests, `ruff` and `mypy`.
- **Reversals, offline and on the throwaway database, on copies,** each restored afterwards. For each, say which test or case fails:
  - `_held_since` removed (the insert alone);
  - the handle's write without its `NOT EXISTS`;
  - `_consume_handle`'s count check removed;
  - `returned` set before the body runs (every failure unknown), and never set (every failure known);
  - a known outcome that leaves its handle;
  - `_hold_for_discard` a no-op;
  - and any other you doubt.
- **The database cases, informational:** the chat suite on a throwaway PostgreSQL under P06.DB's D4, if Docker allows, with any probe you need: two commands holding one reference; a sweep's removal between the handle and the save; a lost commit acknowledgement; a failure of the re-read.

**What comes after this review: the correction classes** (D-07; the manager workflow, step 6). Report every finding with its severity. A correction pass takes every blocking finding, and any should-fix finding that is:
- **a defect in application behaviour:** a command that refuses, saves or discards against D18's custody bullet; a revoke, rotation or transfer of an active registration refused for custody's sake; a deadlock or a crossing;
- **a defect at a security boundary:** a token or a reference anywhere AN1 does not allow; a reference in use discarded; a reference held by no row outside AN1's exception; a custody rule left open; a seal or HDE's boundary crossed;
- **a false claim that a decision or the merge would rest on** (D-07): where that claim is what a decision, an acceptance check, B2's sweep or the merge reads.

A missing test is a correction only when the behaviour is at a security boundary or an acceptance check rests on it. Any other overclaim, and the reach of a static scan, a substring pin or a simulation, is recorded and carried. For each finding, say whether it falls in one of these classes.

**How you work:**
- Nathan started you and will relay your report to the manager, App Manager 13. You are neither the manager nor an implementer.
- You may use any tools, subagents, scheduled wake-ups or other capabilities the review needs, including Claude Code's code-review and security-review capabilities.
- Your boundary is scope: review one exact head and report.
  - **Change nothing** in the repository, on GitHub or in Notion: no commits, pushes, PR comments, thread resolutions, re-runs or workflow dispatches. Read GitHub with the GitHub tools where your session has them, otherwise with `gh api` REST `GET` calls, and say which you used.
  - **Scratch work goes in a copy outside the repository,** never the checkout (DM-14 item 6). Use absolute paths, and confirm afterwards that `git status` is clean.
- **Network:**
  - PyPI and the npm registry, for hash-locked installs from the existing locks in a scratch copy;
  - Docker Hub, only to pull the PostgreSQL image the workflow pins (`postgres@sha256:d74eeac9a635390a49bc21bd49fccd973de707e2a53a76ac49b552b8712ec46f`);
  - GitHub, read only, to read the runs, PR60 and Codex's reviews.

  A page you cannot reach is named as unread, never filled from memory.
- **Local database runs** are allowed only as P06.DB's D4 allows them (`docs/planning/p06-db-disposable-postgres-proof.md`, D4, its four conditions):
  - a throwaway PostgreSQL in Docker, from that image, on loopback only;
  - a generated password, and the run's marker on each database;
  - none of `DATABASE_URL`, `HD_API_KEY`, `GEO_API_KEY` or any `PG*` name present;
  - removed afterwards.

  Migrations reach that database only through the proof's own commands; never run `manage.py migrate` yourself.
- **Never:**
  - dump the environment, or print a credential, password, marker, token, session key or key, the suite's synthetic push tokens included;
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
6. **A clean process environment** for every repository command: `env -i PATH="$PATH" HOME="$HOME" LANG=C.UTF-8`, plus only the command's own variables. No `AWS_*` name passes.

## 2. Start gate

```bash
git fetch origin claude/magical-wozniak-yfmmx2 main
git switch --detach <PROMPT_SHA>
git rev-parse HEAD                                    # must print <PROMPT_SHA>
git merge-base --all origin/main HEAD                 # expected: one line, 988a36a1fe4bc7b654a07e565e15fe721dcf3520
git merge-base --is-ancestor <PROMPT_SHA> origin/claude/magical-wozniak-yfmmx2 && echo "this prompt's commit is on the live branch"
git diff --quiet 48f08017350993c13bccb78095e084ad0434a6a5 HEAD -- . ':!*.md' && echo "the code head under review"
git diff --quiet 48f08017350993c13bccb78095e084ad0434a6a5 origin/claude/magical-wozniak-yfmmx2 -- . ':!*.md' && echo "no code on the live branch after 48f0801"
git show origin/claude/magical-wozniak-yfmmx2:docs/testing/evidence/2026-11-19-sv4-chat-notifications.md | grep -c -E '^#+ Exact-head review of B1-C1'   # must print 0
```

If any check fails, stop and report. The prompt is stale if its commit is not on the live branch, a non-Markdown path changed there after `48f0801`, or this review is already recorded.

**Classify the change** as root `AGENTS.md` requires, with the trusted base policy outside the candidate tree:

```bash
base=$(git rev-parse origin/main); head=$(git rev-parse HEAD)
policy_dir=$(mktemp -d)
git show "$base:scripts/change_scope.py" > "$policy_dir/change_scope.py"
python3 -I "$policy_dir/change_scope.py" --base "$base" --head "$head" --merge-base
```

Run it from the checkout (the policy file outside it). Expected: `"full": true`. Anything else: stop and report.

**Then read, completely, at `HEAD`:**
- root `AGENTS.md` and `CLAUDE.md`; `services/api/README.md`; `proofs/postgres-ordering/README.md`;
- the brief, revision 13: D17, D18 (AN1's custody bullet), D24 (AN2's sentence), D29, "Owned paths" (B1-C1);
- DM-102's report, whole;
- B1-C1's prompt (`docs/ephemeral/2026-11-27-sv4-b1-c1-custody-correction-prompt.md`), its stop rule and section 3 above all;
- the record's sections "Exact-head review of B1", "Dev Manager 7's DM-102", "B1-C1" and "Manager verification of B1-C1", whole;
- the carried-items file's entries for SV4 B2 from B1's review and from B1-C1;
- every file in the code diff, whole, beside its version at `e7e7e84`.

**The runs,** read from GitHub:
- 45941121120, and PR60's run on `<PROMPT_SHA>` if it has finished: every job's conclusion and duration, and the gate's line;
- Codex's review of `<PROMPT_SHA>`, and every thread on PR60.

## 3. What to do

1. Write the threat model, then review the change against the focus, item by item.
2. In a scratch copy of `48f0801`: re-run the checks and the reversals above, and any you doubt; run the database cases locally under D4 if you can, informational.
3. For each finding: its severity (blocking, should fix, nit), its file and line, the evidence, and whether it falls in a correction class.

## 4. Report

Your final message is the report Nathan relays:
- the prompt revision (revision 1, from `<PROMPT_SHA>`), and the start gate's, the classification's and the environment check's results;
- the threat model, each threat with its stopping code and its test or run;
- the focus, item by item, with your verdict on each;
- every finding, with its severity, file and line, evidence and correction class;
- the checks and reversals you re-ran, each with its exact result, and any local run;
- the runs and Codex's reviews as you read them, and which GitHub route you used;
- your verdict: **approve**, **approve with nits** or **changes requested**;
- what you did not read or run, and why.
