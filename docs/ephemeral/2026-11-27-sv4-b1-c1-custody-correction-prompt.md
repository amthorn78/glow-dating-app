# SV4 B1-C1 prompt — the correction: the token's custody (a handle written first)

- **Owner:** App Manager 13. Nathan starts this session manually, in the `Glow App - No Stream` environment (OD-36), and relays its report.
- **Revision 1, 27 November 2026.**
- **Durable brief:** [SV4 — the chat and notifications slice](../planning/sv4-chat-notifications.md), revision 13: D18's custody bullet by DM-102's AN1; D24's pending-discard rule by AN2; "Owned paths (provisional; each prompt completes them)", B1-C1.
- **The findings:** the SV4 record's "Exact-head review of B1" (`docs/testing/evidence/2026-11-19-sv4-chat-notifications.md`), with its disposition and "Dev Manager 7's DM-102".
- **The decision:** [DM-102](../continuity/dev-manager/reviews/2026-11-27-dm-102-sv4-b1-c1-custody.md) (Dev Manager 7, `f86ccaf`), AN1 to AN11.
- **Where the result goes:**
  - the session's changes to the owned paths below, and its section "B1-C1" in the same record, on its own branch;
  - the run of record: the Foundation run on its last code commit;
  - the manager adds its verification to the record, and records the outcome in the brief's "Sessions".
- **Model and reasoning setting** (OD-10, OD-30, OD-33, OD-34, OD-42). The reading is the recommendation; it gates nothing, and Nathan picks.
  - **TypeSafe v8.2: Opus 5.5 at high.** Effort score 2.35 (confidence 0.74); rung probabilities low 0.00, medium 0.02, high 0.62, extra high 0.35, max 0.01, ultracode 0.00. Model probabilities Fable 5.1 0.01, Opus 5.5 0.99, Sonnet 5.5 0.00, Haiku 5.5 0.00 (confidence 0.99). Twenty-four cells, computed from the two answers: Fable 5.1 at low 0.000, Fable 5.1 at medium 0.000, Fable 5.1 at high 0.006, Fable 5.1 at extra high 0.003, Fable 5.1 at max 0.000, Fable 5.1 at ultracode 0.000, Opus 5.5 at low 0.000, Opus 5.5 at medium 0.020, Opus 5.5 at high 0.614, Opus 5.5 at extra high 0.346, Opus 5.5 at max 0.010, Opus 5.5 at ultracode 0.000, Sonnet 5.5 at low 0.000, Sonnet 5.5 at medium 0.000, Sonnet 5.5 at high 0.000, Sonnet 5.5 at extra high 0.000, Sonnet 5.5 at max 0.000, Sonnet 5.5 at ultracode 0.000, Haiku 5.5 at low 0.000, Haiku 5.5 at medium 0.000, Haiku 5.5 at high 0.000, Haiku 5.5 at extra high 0.000, Haiku 5.5 at max 0.000, Haiku 5.5 at ultracode 0.000. Sent 2026-11-27T03:54:46Z. Nathan picks the cell.
- **The Dev Manager's read:** none before it runs. DM-102 decided the design, and this prompt quotes its words. It authorizes no credential use and no live provider action (the charter, "Read before it takes effect"). Under D-07 the correction goes on the list for the Dev Manager's pre-merge read of B1.
- **Environment** (OD-36): `Glow App - No Stream`. No Stream variable is needed, and none may be present. `amthorn78/glow-docs` is attached, read only; this work needs nothing from it (OD-74).
- **It runs alone** (OD-29). Then, in order:
  1. the manager's verification;
  2. PR60's run and Codex's review of its new head;
  3. a full exact-head review of B1-C1, with DM-102's focus (its section 5);
  4. the Dev Manager's pre-merge read of B1;
  5. the merge.
- **Deletion condition:** prune after B1's pull request (PR60) merges and its merge receipt is recorded.

**Manager:** before giving this prompt to Nathan, replace every `<START_SHA>` with the full SHA of the manager-branch commit that holds this revision, and run its start gate against the live branch (AM11-21).

---

You are the **correction session B1-C1** for SV4 B1, for the Glow dating app, in the public repository `amthorn78/glow-dating-app` (public for now; OD-51). Nathan Amthor, its owner, started you manually. This prompt is revision 1, from commit `<START_SHA>` of the manager branch `claude/magical-wozniak-yfmmx2`.

**What came before.**
- **B1** (code head `e7e7e84`; the record's section "B1") built F12's surface: three sealed routes, the persistence port and its ORM adapter `OrmNotificationPersistence` (`services/api/glow_notifications/persistence.py`), migration `0014` and twelve chat-suite cases. Run of record 45900925199 passed all twelve jobs, the chat suite 30/30. PR60 carries it into `main`, which is at `988a36a`.
- **B1's exact-head review** (the record's "Exact-head review of B1") found F12's behaviour right on every route, and asked for changes to the token's custody:
  - **B1R-1** (Codex's P2, comment 4713760650; confirmed on a database). `device()` calls the store's `put` before `_run`, then parks the fresh reference whenever `done is None or not done.saved` (lines 460 and 461). `_park` catches every failure of its insert and only logs (370 to 376), so with the database unreachable for that statement, the reference is held by no row.
  - **B1R-2** (Codex's second P2, comment 4715163584). `_run` answers `done=None` for a rollback and for a failure at the commit alike. After a commit whose acknowledgement is lost, a reference that a registration holds is also parked. The owner's later revoke, rotation or transfer then fails the pending discards' uniqueness in `_hold_for_discard`, and B2's sweep would discard a token in use.
  - **B1R-3.** With `_hold_for_discard` a no-op, all 94 of B1's offline tests and all twelve of its cases pass.
  - **B1R-4, B1R-6 and B1R-7** (nits, taken here because the correction changes their files):
    - B1R-4: "never logged" holds for the application, not the database server's own log;
    - B1R-6: two of the record's sentences, on a first register's `state_conflict` and a transfer's timing, are too wide;
    - B1R-7: `production-contracts.md`'s codes bullet reads as if a device command with no token store were retryable.
  - **B1R-5** (a nit): the port does not say `put` returns a fresh reference each time. AN11 states it.
- **DM-102** (Dev Manager 7; the record's "Dev Manager 7's DM-102") chose **(b): the new reference's pending discard is written as its handle before the command's transaction, and the transaction that saves the reference consumes it.** It set three conditions (AN1), now D18's custody bullet in the brief's revision 13, which section 3 quotes. It also set the sweep's rule (AN2, D24's, for B2: you build no sweep), and the words AN3 to AN8 and AN11, which you apply as given.
- **The rest** of the review's findings are carried or recorded (the disposition table): you do not take them up. Codex's two threads are resolved by the manager once your fix and Codex's review of your head confirm it; you do not touch them.

**This correction changes the device command's custody paths, the docstrings that state them, the fixture token store, the tests and cases that prove them, and the words DM-102 gives.** The following stay exactly as they are:
- the routes, the views, the lock order and every check other than the custody paths;
- the idempotency digest, the bound, the settings command and the read;
- the models and the migration (no migration change: `PendingTokenDiscard` already has `created_at`);
- `glow_chat`, `glow_identity`, `glow_profiles`, `glow_discovery` and `glow_api`;
- the workflow, the contract's JSON and the generated outputs;
- every other suite.

**How you work:**
- Nathan started you and will relay your report to the manager, App Manager 13. You are neither the manager nor a reviewer.
- You may use any tools, subagents, scheduled wake-ups or other capabilities the work needs.
- **Your boundary is scope:**
  - write only these paths (the brief's revision 13, "Owned paths", B1-C1):
    - `services/api/glow_notifications/persistence.py`: the custody paths (`_run`'s outcome split, the handle, the save's count check, the immediate discards) and the module docstring's "Custody" paragraph;
    - `services/api/glow_notifications/contract.py`: `REFUSALS`, only for a reason the correction adds;
    - `services/api/glow_domain/notifications.py`: `TokenStore`'s docstring (AN11), and a reason constant the correction adds, only;
    - `services/api/glow_domain/notification_fixtures.py`: `FixtureTokenStore`, a way to return a reference it already gave out, only;
    - `services/api/glow_persistence/models.py`: `PendingTokenDiscard`'s docstring, only;
    - `services/api/tests/test_notifications_routes_offline.py`, `test_notifications_port.py` and `test_notifications.py`, as the correction's tests need;
    - `proofs/postgres-ordering/glow_ordering_proof/chat_cases.py`, `chat_support.py` and `chat_suite.py`, for the new cases and their hold points;
    - `proofs/postgres-ordering/tests/test_chat_offline.py`: the case count's pin and the plan tests, only as the new cases need;
    - `proofs/postgres-ordering/README.md`: the chat suite's paragraph (its cases and their count), only;
    - `docs/architecture/production-contracts.md`: AN3, AN4 and B1R-7's sentence, only;
    - `docs/architecture/data-model.md`: AN5 to AN7, only;
    - the record: AN8 in section "B1", and your own section "B1-C1";
  - push only your own session branch, with `git push -u origin <branch>`. Never push `main`, the manager branch or `claude/dev-manager`, and never delete a branch;
  - on GitHub, read only: use the GitHub tools where your session has them, otherwise `gh api` REST `GET` calls, and say in the report which you used. No pull request, comment, review, thread resolution, re-run, workflow dispatch or setting. Change nothing in Notion.
- **The stop rule.** Stop and report, with no further change, if any of these holds:
  - **a path:** the work needs any path or passage outside the list above, such as the migration, a model's field or constraint, `views.py`, `providers.py`, another app, the workflow, the contract's JSON, a generated file, another suite or the CI policy;
  - **the decision:**
    - AN1 cannot be met without changing the lock order, a model or the migration;
    - a reason the correction adds would need a code other than `state_conflict` (the save's count check) or `token_store_refused`'s (a reference already held);
    - the known and unknown outcomes cannot be told apart at the point AN1 names (whether the failure arose before or after the transaction's body returned);
  - **an earlier test:** a test or case not named in section 3, item 9, would have to change, or a named one would change beyond what that item says;
  - **the words:** an old passage of AN3 to AN8 or AN11 is not found exactly once at `<START_SHA>`;
  - **a proof or a reversal:** a result in section 3 differs from the one it names.
  - In each case, report it; do not narrow this prompt's words to pass it. A reversal's temporary edit is allowed, and must be undone.
- **No switch in the adapter.** B1's adapter has no test-only branch, flag or hook that changes a lock, a check or a write (its module docstring), and the correction adds none. The cases simulate a failure from the suite's side, in `chat_support.py`; the record names each simulation, what it stands for and what it cannot show.
- **The push rule** (AM5-04).
  - After you push a code commit, push nothing more to your branch until that commit's Foundation run has finished. A newer push cancels the earlier run's application jobs, and the run of record is lost.
  - Push your records commit only after the run of record has finished.
  - The workflow runs on pushes to `claude/**` and `ccr-**`; if your branch is named otherwise, say so in the report, since no run starts.
  - **If GitHub never starts the run** (it stays `queued` with no jobs for 30 minutes), do not re-run it, dispatch it, push an empty commit, or ask anyone to re-run it (OD-58). Record it, push your records commit, and report.
  - **If the run fails,** stop and report the failing job and its log lines. Do not re-run it.
- **Network:**
  - PyPI, for `pip install --require-hashes` from the existing locks;
  - Docker Hub, only to pull the PostgreSQL image the workflow pins (`postgres@sha256:d74eeac9a635390a49bc21bd49fccd973de707e2a53a76ac49b552b8712ec46f`);
  - GitHub, read only.

  The environment does not enforce this; you do.
- **Local database runs** are iteration, not evidence. They are allowed only as P06.DB's D4 allows them (`docs/planning/p06-db-disposable-postgres-proof.md`, D4, its four conditions):
  - a throwaway PostgreSQL in Docker, from that image, on loopback only;
  - generated passwords and markers, never printed;
  - none of `DATABASE_URL`, `HD_API_KEY`, `GEO_API_KEY` or any `PG*` name in any process environment;
  - removed afterwards.

  Migrations reach that database only through the proof's own commands; never run `manage.py migrate` yourself. The evidence of record is CI's run.
- **Never:**
  - dump the environment, or print, echo, log, copy or commit any credential, password, marker, token or key, the suite's synthetic push tokens included;
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
git diff --quiet e7e7e845946da1a3aa46f5fcf56add24e99dc70b HEAD -- . ':!*.md' && echo "B1's code head"
git diff --quiet e7e7e845946da1a3aa46f5fcf56add24e99dc70b origin/claude/magical-wozniak-yfmmx2 -- . ':!*.md' && echo "no code on the live branch after e7e7e84"
grep -c -E '^#+ Exact-head review of B1' docs/testing/evidence/2026-11-19-sv4-chat-notifications.md   # must print 1
grep -c -E '^#+ B1-C1' docs/testing/evidence/2026-11-19-sv4-chat-notifications.md                     # must print 0
```

If a check fails, stop and report. The prompt is stale if its commit is not on the live branch, a non-Markdown path changed there after `e7e7e84`, or a B1-C1 section already exists.

**Then read, completely:**
- root `AGENTS.md` and `CLAUDE.md`; `services/api/README.md`; `proofs/postgres-ordering/README.md`;
- the record's sections "B1" ("The threat model's inputs" and "Limits and deviations" above all), "Manager verification of B1", "Codex on PR60", "Exact-head review of B1" (with its disposition) and "Dev Manager 7's DM-102", whole;
- DM-102's report (`docs/continuity/dev-manager/reviews/2026-11-27-dm-102-sv4-b1-c1-custody.md`), sections 3 to 6 and 9, whole;
- the brief, revision 13: D17, D18 (AN1's custody bullet), D19, D24 (AN2's sentence), D29, "Owned paths" (B1-C1), and "Acceptance checks (Stage B)";
- `services/api/glow_notifications/persistence.py` and `contract.py`, whole;
- `services/api/glow_domain/notifications.py`'s `TokenStore`, `ProviderToken` and `TokenReference`; `notification_fixtures.py`'s `FixtureTokenStore`;
- `PendingTokenDiscard` and `DeviceRegistration` in `services/api/glow_persistence/models.py`;
- `services/api/tests/test_notifications_routes_offline.py`, whole;
- `proofs/postgres-ordering/glow_ordering_proof/chat_cases.py`'s twelve `notifications.*` cases, `chat_support.py`'s `ObservedTokenStore` and hold points, and `proofs/postgres-ordering/tests/test_chat_offline.py`'s `ChatPlanTests`.

## 3. What to do

**The rule** (D18's custody bullet, revision 13, DM-102's AN1, as given; every item below implements it):

```text
The store's `put` runs before the command's transaction, never inside it, so no external call holds a lock. **Its handle comes first** (B1-C1; DM-102): before the transaction, the new reference's pending discard is written in its own statement, and only if no registration and no pending discard already holds that reference; a reference already held is the store's refusal (`token_store_refused`) and is not discarded, and if the write fails the store discards the reference at once and the command answers its error. The transaction that saves the reference on a registration deletes its pending discard, and refuses (`state_conflict`) unless it deletes exactly that one row. A command whose outcome is known and did not save the reference (a refusal, a deadlock, a replay, or a failure raised before the transaction's body returned) discards it at once, as a retired one is; one whose outcome is unknown (a failure after the body returned, at the commit) leaves the handle to D24's sweep. So every reference the store holds has a registration or a pending discard, except after a process stop, or a failed write and a failed discard, between the `put` and the handle.
```

1. **`_run`'s outcome split (AN1, its third condition).**
   - `_run` tells a **known** outcome, a failure raised before the transaction's body returned, from an **unknown** one, a failure after the body returned (at the commit, as the transaction's block exits).
   - Known failures include:
     - a refusal;
     - a deadlock;
     - a database error inside the body, the one-active-row constraint's `IntegrityError` included (case 9's race).
   - `device()` reads the split from `_run`'s result. Say in `_run`'s docstring where the split falls.
   - The read and the settings command keep their answers; the split changes no code a caller is served.
2. **The handle (AN1, its second condition).** In `device()`, after the store's `put` and before `_run`, write the fresh reference's `PendingTokenDiscard` row in its own statement, outside any transaction, and only if no `DeviceRegistration` and no `PendingTokenDiscard` already holds that reference.
   - **A reference already held:** the command refuses `token_store_refused`, discards nothing, and writes nothing. The reference belongs to another holder.
   - **A failed write:** the store discards the reference at once, and the command answers its error.
     - If that discard fails too, log one fixed line, never a value.
   - **Which failure is which:** say how the write tells a reference already held (the pending discards' uniqueness, or a registration found) from a failed write, under concurrency as well as alone.
   - **No `_park`:** `_park` goes; nothing parks a reference after the transaction any more.
3. **The save consumes its handle (AN1, its first condition).** The transaction that saves the reference on a registration (a first registration's `create`, and a rotation's or a re-registration's `update`) deletes the handle's row. It refuses unless the delete removes exactly one row.
   - The refusal is a reason the correction adds, mapped to `state_conflict` (409, not retryable) in `REFUSALS`.
   - `MappingCompletenessTests` reaches the new reason.
   - **Where in the order:** the delete runs under the command's locks, after the registrations' locks, so the lock order stays the account, the session, the registrations, then the handle's row. Say whether any path can deadlock against B1's other commands.
4. **The immediate discards (AN1).**
   - **A known outcome that did not save the reference** (a refusal, a deadlock, a replay, or a failure raised before the transaction's body returned) discards the reference at once through `_discard`, as a retired one is. The store discards it, then its handle's row is removed; a failed discard leaves the row for B2's sweep.
   - **An unknown outcome** leaves the handle and discards nothing.
   - A retired reference's path (`_hold_for_discard` in the transaction, `_discard` after the commit) is unchanged.
5. **The docstrings.** They state AN1's rule in the same terms as the brief:
   - the adapter's module docstring, its "Custody (AM4)" paragraph;
   - `PendingTokenDiscard`'s docstring;
   - `TokenStore`'s, by AN11, as given.

   Keep the module docstring's "There is no switch" paragraph true.
6. **The fixture store.** `FixtureTokenStore` gains a way to return, on its next `put`, a reference it already gave out, as `refuse_next_put` and `fail_next_discard` inject theirs. Its environment guard is unchanged.
   - Its `put` already returns a new reference for every call, and its `discard` of an unknown reference changes nothing (AN11); a port test pins both if none does.
7. **Offline tests**, in `test_notifications_routes_offline.py`, in the style of `test_the_store_takes_the_token_before_the_commands_transaction`:
   - the handle's write follows the `put` and precedes `_run` in `device()`;
   - the save's delete checks its count;
   - `test_the_store_takes_the_token_before_the_commands_transaction`'s assertion on `self._park(fresh)` (line 915) changes to the handle's write, and its other assertions stay.

   Say what each structure test reads and what it would miss, as B1's record does for its pins.
8. **Database cases** in the chat suite, each with its reversal (section 3, item 11). They run before `notifications.no_token_in_any_row_or_answer`, which runs after every other F12 case and checks each reference the store issued, theirs included, and must pass unchanged; and before the cases that publish a cause `hidden`, so `test_the_cases_that_publish_hidden_run_last` stays true.
   1. **A failed discard waits (B1R-3).** With the fixture store's `fail_next_discard`, a rotation, a revoke and a transfer each leave the retired reference in the pending discards, with its token still held by the store, and the registration's row without it.
   2. **The handle's write failing.** The handle's write fails (simulated from the suite's side): the store discards the reference, nothing is saved, no row holds it, and the command answers `state_conflict`.
   3. **A known refusal discards at once.** A register refused inside the transaction (a stale version, and the bound): the store no longer holds its token, and no pending discard is left. Likewise a replay's reference.
   4. **An unknown outcome after the commit** (B1R-2's proof; simulated, as the review did: the commit runs, then the command sees a failure).
      - The registration is `active` with the reference, and the reference is not pending.
      - A later revoke by the owner is accepted, and discards the token.
   5. **A save that finds its handle gone refuses.** At the transaction's start (the probe's `on_begin`), another connection removes the handle's row, as B2's sweep would.
      - The command refuses `state_conflict`, and no registration holds the reference.
      - The case then discards the reference through the store, as the sweep would after removing the row (AN2), so no token is left held by no row.
   6. **A reused reference is refused.** The fixture store returns a reference an active registration already holds.
      - The command refuses `token_store_refused`, and nothing is written.
      - The earlier holder's registration is unchanged, and its token is still held.
   7. **A failure inside the transaction is known.** In case 9's race (two accounts registering one new installation), the losing command's reference is discarded at once, and no pending discard is left.

   Four of B1's cases today expect a refused, replayed or losing register's reference "in the pending discards": `notifications.replay_and_conflict`, `bound_of_active_registrations`, `register_refused_once_its_sessions_sign_out_commits` and `two_accounts_one_new_installation` (`chat_cases.py`, lines 1675, 1704, 1790, 1810, 1833, 1849, 1863 and 1884). Under AN1 each is discarded at once: those expectations change to "the store no longer holds the token, and no pending discard is left", and nothing else in those cases changes.
9. **The earlier tests that may change, and how:**
   - **the four cases above:** their pending-discard expectations, as item 8 says, and their docstrings' sentences on it;
   - **`test_the_store_takes_the_token_before_the_commands_transaction`:** its `_park` assertion, as item 7 says;
   - **`MappingCompletenessTests`:** it gains the new reason;
   - **`test_chat_offline.py`:** the case count's pin (30 to 37) and the plan;
   - **the proof README's chat paragraph:** the count and the new cases.

   Any other test that would have to change is a stop.
10. **The words, as given.** Apply each pair below by script: find the old passage exactly once at `<START_SHA>`, replace it, and check the new passage then occurs exactly once. Record the check.

**AN3** (`docs/architecture/production-contracts.md`). Replace:

```text
a command that does not save it (a refusal, a failure or a replay) leaves the reference in the pending discards, and an old one is discarded after the commit.
```

with:

```text
before the transaction the reference's pending discard is written as its handle, and the transaction that saves the reference deletes it, so a reference the store holds has a registration or a pending discard, except after a process stop, or a failed write and a failed discard, between the `put` and the handle (SV4 B1-C1; DM-102). A command that does not save the reference discards it at once when its outcome is known (a refusal, a deadlock, a replay, or a failure before its transaction's body returned), and leaves it to SV4 B2's sweep when the outcome is unknown (a failure at the commit); an old one is discarded after the commit, and a failed discard waits for the sweep.
```

**AN4** (`docs/architecture/production-contracts.md`). Replace:

```text
so it is never served, logged or shown, and the app makes it at random for each installation (P09.2; DM-101's AM7).
```

with:

```text
so Glow's application never serves, logs or shows it, and the app makes it at random for each installation (P09.2; DM-101's AM7); the database server's own log is the P11 plan's (B1R-4).
```

**AN5** (`docs/architecture/data-model.md`). Replace:

```text
the token goes to the token store before the command's transaction, and only the reference is kept (SV4 B1, D18; DM-101's AM4).
```

with:

```text
the token goes to the token store before the command's transaction, and only the reference is kept; its pending discard is written first and deleted by the transaction that saves it (SV4 B1, D18; DM-101's AM4; DM-102).
```

**AN6** (`docs/architecture/data-model.md`). Replace:

```text
the installation identifier is never served, logged or shown (AM7).
```

with:

```text
Glow's application never serves, logs or shows the installation identifier (AM7; the database server's log is the P11 plan's, B1R-4).
```

**AN7** (`docs/architecture/data-model.md`). Replace:

```text
one a command did not save (a refusal, a failure or a replay), for SV4 B2's sweep, or one it retired, until the store discards it after the commit, a failed discard staying for the sweep.
```

with:

```text
the handle a command writes for its new reference before its transaction, which the transaction that saves the reference deletes, and which a known refusal, deadlock, replay or earlier failure discards at once, an unknown outcome leaving it for SV4 B2's sweep; or one a command retired, until the store discards it after the commit, a failed discard staying for the sweep (DM-102).
```

**AN8** (`docs/testing/evidence/2026-11-19-sv4-chat-notifications.md`). Replace:

```text
and a fresh reference a command did not save is parked, not discarded at once, so it waits for B2's sweep.
```

with:

```text
and a fresh reference a command did not save is parked, not discarded at once, so it waits for B2's sweep. (Superseded by B1-C1, DM-102: the handle is written before the transaction, so only a stop, or a failed write and a failed discard, between the `put` and the handle leaves a reference in no row; a known refusal or replay discards its reference at once, and an unknown outcome leaves its handle for the sweep.)
```

**AN11** (`services/api/glow_domain/notifications.py`). Replace:

```text
    """Where a push token is kept. ``put`` returns the reference or raises ``TokenStoreError``;
    ``discard`` removes a stored token or raises ``TokenStoreError``. The domain never resolves a
    reference."""
```

with:

```text
    """Where a push token is kept. ``put`` returns a reference it has never returned before, even
    for a token it already holds, or raises ``TokenStoreError``; ``discard`` removes the token a
    reference holds, changes nothing for a reference already discarded, or raises
    ``TokenStoreError``. The domain never resolves a reference."""
```

**B1R-7** (`docs/architecture/production-contracts.md`, the codes bullet). Replace:

```text
the token store's refusal is `provider_unavailable` (503, retryable), and so is a device command when no token store is configured;
```

with:

```text
the token store's refusal is `provider_unavailable` (503, retryable), and a device command when no token store is configured is `provider_unavailable` (503, not retryable);
```

11. **Reversals.** Make each on a copy, offline where it can be shown and on the throwaway database otherwise, and restore it byte for byte. Record which test or case fails:
    - `_hold_for_discard` a no-op: case 8.1 fails;
    - the handle's write failure not discarding: case 8.2;
    - a known refusal leaving its handle: case 8.3;
    - an unknown outcome discarding the reference: case 8.4;
    - the save without its count check: case 8.5 and the structure test;
    - the handle written without its condition: case 8.6;
    - every error treated as unknown: case 8.7;
    - the handle's write moved after `_run`: the structure test;
    - B1's r05 (the `put` inside the transaction) still fails its test;
    - any other you doubt.
12. **The record, section "B1-C1".**
    - What changed, by item; the commands and their results; the reversals; the run of record.
    - Its limits: the custody limit that stands (AN1's last sentence); each simulation and what it cannot show; whatever the structure tests miss.
    - **"What B1-C1 changes in section B1":** B1's custody sentence in "The threat model's inputs" ("A reference the command does not save goes to the pending discards after the transaction"); B1R-6's two sentences on a first register's `state_conflict` and a transfer's timing, in the review's narrower terms; AN8's mark. B1's section otherwise keeps B1's words (DM-100's AL4 and AL5).

## 4. Checks

In the API's virtual environment (from its own lock, with `--require-hashes`, under `env -i`):
- `GLOW_ENV=test python manage.py check && GLOW_ENV=test python manage.py test tests`;
- `ruff check .`, `ruff format --check .` and `mypy`, and `mypy glow_notifications` by name, since CI's list does not name it;
- `GLOW_ENV=test python manage.py makemigrations --check --dry-run` ("No changes detected").

In the ordering proof's: its offline tests, `ruff` and `mypy`. Then the chat suite on a throwaway database under D4, if Docker allows (iteration only).

Then push the code commit, and read its Foundation run: every job's conclusion and the gate's line, the chat job's case count and both scans. Then the records commit.

## 5. Report

Your final message is the report Nathan relays:
- the prompt revision (revision 1, from `<START_SHA>`), the start gate's and the environment check's results;
- your branch, the code head and the records head, and the run of record with each job's conclusion and the chat job's counts;
- what changed, by item 1 to 12, with each file;
- each new case and test, with its reversal's result;
- the words applied, with the script's check;
- every limit and deviation, and anything this prompt got wrong;
- which GitHub route you used;
- NOTHING NEEDED, or what is needed and from whom.
