# SV4 B2 prompt — the triggers, the notification deliverer, `logout`, the sweeps and G-04's read

- **Owner:** App Manager 13. Nathan starts this session manually, in the `Glow App - No Stream` environment (OD-36), and relays its report.
- **Revision 1, 27 November 2026.**
- **Durable brief:** [SV4 — the chat and notifications slice](../planning/sv4-chat-notifications.md), revision 14, its section "Stage B" (D21 to D27, D29's B2 cases, D30, D31; B2's owned paths, completed in this prompt).
- **Where the result goes:**
  - the session's code on its own branch, and its section "B2" in the SV4 record (`docs/testing/evidence/2026-11-19-sv4-chat-notifications.md`);
  - the run of record: the Foundation run on its last code commit;
  - the manager adds its verification to the record, and records the outcome in the brief's "Sessions".
- **Model and reasoning setting** (OD-10, OD-30, OD-33, OD-34, OD-42). The reading is the recommendation; it gates nothing, and Nathan picks.
  - **TypeSafe v8.2: Opus 5.5 at extra high.** Effort score 3.07 (confidence 0.61); rung probabilities low 0.00, medium 0.03, high 0.19, extra high 0.51, max 0.21, ultracode 0.06. Model probabilities Fable 5.1 0.23, Opus 5.5 0.76, Sonnet 5.5 0.01, Haiku 5.5 0.00 (confidence 0.68). Twenty-four cells, computed from the two answers: Fable 5.1 at low 0.000, Fable 5.1 at medium 0.007, Fable 5.1 at high 0.044, Fable 5.1 at extra high 0.117, Fable 5.1 at max 0.048, Fable 5.1 at ultracode 0.014, Opus 5.5 at low 0.000, Opus 5.5 at medium 0.023, Opus 5.5 at high 0.144, Opus 5.5 at extra high 0.388, Opus 5.5 at max 0.160, Opus 5.5 at ultracode 0.046, Sonnet 5.5 at low 0.000, Sonnet 5.5 at medium 0.000, Sonnet 5.5 at high 0.002, Sonnet 5.5 at extra high 0.005, Sonnet 5.5 at max 0.002, Sonnet 5.5 at ultracode 0.001, Haiku 5.5 at low 0.000, Haiku 5.5 at medium 0.000, Haiku 5.5 at high 0.000, Haiku 5.5 at extra high 0.000, Haiku 5.5 at max 0.000, Haiku 5.5 at ultracode 0.000. Sent 2026-11-27T07:16:30Z. Nathan picks the cell.
- **The Dev Manager's read:** none before it runs. Stage B's design was read as DM-101, and DM-102's and DM-103's conditions are applied as given in revisions 13 and 14. This prompt authorizes no credential use and no live provider action. Dev Manager 7 reads B2 before its pull request merges (D-07), with the CI policy's line 13, which B2 changes (governing Markdown).
- **Environment** (OD-36): `Glow App - No Stream`. No Stream variable is needed, and none may be present. `amthorn78/glow-docs` is attached, read-only; this work needs nothing from it (OD-74).
- **It runs alone** (OD-29). Then, in order:
  - the manager's verification;
  - a new pull request from the manager branch, its run and Codex's review;
  - B2's exact-head code and security review, with its threat model;
  - any correction under D-07;
  - Dev Manager 7's pre-merge read;
  - the merge. Its receipt closes "Carried to SV4" (D30).
- **Deletion condition:** prune after B2's pull request merges and its merge receipt is recorded.

**Manager:** before giving this prompt to Nathan, replace every `<START_SHA>` with the full SHA of the manager-branch commit that holds this revision, and run its start gate against the live branch.

---

You are the **implementation session for SV4 B2**, for the Glow dating app, in the public repository `amthorn78/glow-dating-app` (public for now; OD-51). Nathan Amthor, its owner, started you manually. This prompt is revision 1, from commit `<START_SHA>` of the manager branch `claude/magical-wozniak-yfmmx2`.

**What B2 is.** The second and last of SV4 Stage B's sessions: the server side of notifications after F12's surface. It runs in process under the proof, sealed until integration. B2 covers:
- **D21, the triggers:** `notify_match` from SV3's like and `notify_message` from the chat deliverer's receipt, each an outbox event of the new schema `glow-notifications-1`, written in the transaction that makes the fact;
- **D22, the notification deliverer:** lease and check, call, receipt, on the chat deliverer's pattern;
- **D23, F12's `logout`:** the deliverer also takes `session_revoked` and `session_expired`, and revokes that session's registrations;
- **D24, the sweeps:** expired sessions, inert registrations, the ledger's retention and the pending discards' retry, in one sealed entry point run by one management command;
- **D25, the ledger's use:** the fixed devices and the sends, its bound and its retention;
- **D26:** no notification tells a block from an unmatch;
- **D27, G-04's read:** `message_recipients(sender)`, with no new table;
- **D29's B2 cases,** in the chat suite;
- **the items carried to B2** from B1's and B1-C1's records and reviews (below).

B2 adds no route, no model field, no migration and no change to the contract. There is no provider call, deployed URL, real member, HDE call, real token or stored credential. The token store and the push transport keep their fixtures, reached through B1's factories (`GLOW_NOTIFICATIONS_TOKEN_STORE`, `GLOW_NOTIFICATIONS_PUSH_TRANSPORT`), which only the proof's chat settings name. The runtime stays sealed. SV5 composes the worker and the schedule.

**The brief, revision 14, is the specification:** the section "Stage B", D21 to D27, D29 (B2), D30, D31, the owned paths, the exclusions, the acceptance checks and the review plan. Much of its text is the Dev Manager's words (DM-101's AM1 to AM16; D18's custody sentences and D24's sweep are DM-103's AO1 and AO2). Follow them exactly. Where this prompt summarizes the brief, the brief wins. Where it adds to the brief, it says so.

**What came before.**
- **SV4 Stage A merged** with PR57, PR58 and PR59 (`988a36a`). **B1 merged** with its correction B1-C1 in PR60 (`1310896`, 27 November 2026), after DM-102 and DM-103. `main`'s push run 45954918003 passed all twelve jobs, the chat suite 37/37.
- **What B1 built,** which you build on:
  - the app `services/api/glow_notifications/` (`apps`, `conf`, `contract`, `persistence`, `providers`, `urls`, `views`), sealed;
  - migration `0014`: `DeviceRegistration` (one row per account and installation, `session`, `ended_by`), `NotificationSettings`, the ledger `NotificationLedgerEntry` (a row per event and installation, `pending` or `sent`) and `PendingTokenDiscard`, each custody rule a database constraint;
  - the ORM adapter's commands, with the token's custody as B1-C1 left it (the handle before the transaction, `_held_since`, the save's count check, `token_handle_missing`, `_run`'s known and unknown outcomes);
  - F12's three routes, and nineteen cases in the chat suite.
- **`main` is at `1310896`.** The manager branch has changed only Markdown since.

**How you work:**
- Nathan started you and will relay your report to the manager, App Manager 13. You are neither the manager nor a reviewer.
- You may use any tools, subagents, scheduled wake-ups or other capabilities the work needs.
- **Your boundary is scope:**
  - write only B2's owned paths:
    - `services/api/glow_notifications/`: new modules for the deliverer, the sweeps and the G-04 read, and `management/commands/` with one command (its `__init__.py` files included). In `persistence.py`, only two things: the docstrings named below, and a helper that the deliverer's `logout` or the sweep shares with the commands' retire path, with every command's behaviour unchanged. `contract.py`, `views.py`, `urls.py` and `providers.py` are unchanged;
    - `services/api/glow_domain/notifications.py`: the schema's and the four event types' constants (below), and whatever the composer needs to take the ORM's facts. Every assertion of `tests/test_notifications.py` is kept, and the module's imports stay the standard library, `.chat` and `.provider_fixtures`. `notification_fixtures.py` changes only if a case needs the fixture transport to fail or to answer `repeat`; record it;
    - `services/api/glow_discovery/interactions.py`: the like's one event, in `interact`, after `activate_reciprocal` applies (D21);
    - `services/api/glow_chat/delivery.py`: the receipt's one event, in `accepted`, in the transaction that marks the submission `accepted` (D21);
    - `services/api/glow_persistence/models.py`: `PendingTokenDiscard`'s docstring only. No field, constraint or migration; `makemigrations --check` stays clean;
    - `services/api/pyproject.toml`: `glow_notifications` added to mypy's `files` list (B1's limit; AM13-15), and nothing else;
    - `services/api/tests/` (B2's new tests, and the earlier tests listed below);
    - the chat suite: `proofs/postgres-ordering/glow_ordering_proof/chat_cases.py`, `chat_support.py`, `chat_suite.py`, `chat_scan.py` and `chat_settings.py` (only as B2's cases need), and `row_locks.py` only if its lists change; `proofs/postgres-ordering/tests/` (the chat suite's offline tests and the earlier tests listed below); `proofs/postgres-ordering/README.md` (the chat suite's row in the module table, its run paragraph and its paragraph of cases);
    - `docs/operations/ci-and-branch-policy.md`, line 13 only (the chat job's paragraph), which is governing Markdown;
    - `docs/architecture/data-model.md` (the notification, device, ledger and outbox lines) and `docs/architecture/production-contracts.md` ("F12 on the server": B2's lines, and the codes bullet below);
    - each file a follow-up below names, only for that follow-up;
    - the record, section "B2" only;
  - push only your own session branch, with `git push -u origin <branch>`. Never push `main`, the manager branch or `claude/dev-manager`, and never delete a branch;
  - on GitHub, read only: use the GitHub tools where your session has them, otherwise `gh api` REST `GET` calls, and say in the report which you used. No pull request, comment, review, thread resolution, re-run, workflow dispatch or setting. Change nothing in Notion.
- **The stop rule.** Stop and report, with no further change, if any of these holds:
  - **an owned path:** the work needs a path outside the list above. That includes `services/api/glow_api/`; any other file in `glow_chat/` (`contact.py`, `events.py`, `reads.py`, `route_reads.py`, `views.py`, `contract.py`, `urls.py`); any other file in `glow_discovery/`; `glow_identity/`; `glow_profiles/`; a migration; `packages/contracts/`; `apps/mobile/`; `scripts/`; `.github/`; an environment template; or a `requirements` file;
  - **a served route:** the work would add a route to the runtime's URL configuration, a path to the production catalog, a module the runtime's settings or WSGI application import, or a management command the runtime's settings list (D31's seal);
  - **a design point** would have to change. These are:
    - D21's two writers, the transactions they write in and the recipients (the like's target; the match's other member);
    - `activate_reciprocal`, which A1 pins by digest, and chat's `events.DELIVERED`;
    - D22's lease, check, call and receipt: the check's facts read under share locks in the lease's transaction; the ledger key as the transport's idempotency key; P06.3's content; a retried event's `available_at` moved by its backoff;
    - D23's consumer of the two session events;
    - D24's three steps for a pending discard, its rule for every writer of a non-null `token_secret_ref`, and the order of the other sweeps;
    - D25's bound (10 active registrations) and retention (30 days);
    - D26's one refusal for a match that is not `active`;
    - D27's read with no new table;
  - **an import:** the deliverer, or any other `glow_notifications` module, would need to import from `glow_chat` or `glow_discovery`. B1's `test_no_module_imports_the_runtime_or_another_slices_routes` forbids it, and B2 keeps it. Or a writer in `glow_chat` or `glow_discovery` would need to import from `glow_notifications`;
  - **a token:** a push token is found in any row, log line, answer, exception or receipt, or a reference anywhere D18 does not allow, or a push's content holds anything P06.3's does not;
  - **a dependency:** a new Python or npm package, or a changed pin (D13);
  - **the timeout:** the chat job, or any other job, no longer fits its `timeout-minutes`;
  - **an earlier test** changes in a way the list below does not allow, or would be weakened or deleted;
  - **a provider:** the token store or the transport would need anything but its fixture, reached through B1's factories.
  - In each case, report it; do not narrow the brief's words to pass it. A reversal's temporary edit is allowed, and must be undone.
- **The push rule** (AM5-04). After you push a code commit, push nothing more to your branch until that commit's Foundation run has finished. A newer push cancels the earlier run's application jobs, and the run of record is lost. Push your records commit only after the run of record has finished. The workflow runs on pushes to `claude/**` and `ccr-**`; if your branch is named otherwise, say so in the report, since no run starts.
  - **If GitHub never starts the run** (it stays `queued` with no jobs for 30 minutes), do not re-run it, dispatch it, push an empty commit, or ask anyone to re-run it (OD-58). Record it, push your records commit, and report.
  - **If the run fails,** stop and report the failing job and its log lines. Do not re-run it, and push no fix without saying so in the report.
- **Network:** PyPI and the npm registry, for `pip install --require-hashes` and `npm ci --ignore-scripts` from the existing locks only; Docker Hub, only to pull the PostgreSQL image the workflow pins, for a local run (below); GitHub, for your pushes and reads. The environment does not enforce this; you do. A page you cannot reach is named as unread, never filled from memory.
- **Local database runs** are allowed only as P06.DB's D4 allows them (`docs/planning/p06-db-disposable-postgres-proof.md`, D4, its four conditions):
  - a throwaway PostgreSQL in Docker, from the pinned image, on loopback only;
  - a generated password, and the run's marker on each database;
  - none of `DATABASE_URL`, `HD_API_KEY`, `GEO_API_KEY` or any `PG*` name present;
  - removed afterwards.
  - Migrations reach that database only through the proof's own commands; never run `manage.py migrate` yourself. Local passes are "iteration, not evidence"; the run of record is CI's.
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
git merge-base --is-ancestor 13108961f5fb3989c72d6a9291e8a163f15a7226 HEAD && echo "PR60's merge present"
git diff --quiet 13108961f5fb3989c72d6a9291e8a163f15a7226 HEAD -- . ':!*.md' && echo "main's code"
git diff --name-only <START_SHA> origin/claude/magical-wozniak-yfmmx2 -- services/api proofs packages apps .github docs/operations/ci-and-branch-policy.md docs/architecture docs/planning/sv4-chat-notifications.md   # must print nothing
grep -c '^## B2' docs/testing/evidence/2026-11-19-sv4-chat-notifications.md   # must print 0
test ! -e services/api/glow_notifications/management && echo "no management command yet"
grep -c 'glow_notifications' services/api/pyproject.toml                       # must print 0
```

If a check fails, stop and report. The prompt is stale if its commit is not on the live branch, the live branch has changed an owned path or the brief since it, or B2's record or command already exists.

**Then read, completely:**
- **The instructions:** root `AGENTS.md` and `CLAUDE.md`; `services/api/README.md`; `proofs/postgres-ordering/README.md`; `docs/operations/ci-and-branch-policy.md`, the database proof jobs' paragraphs.
- **The brief,** revision 14: the section "Stage B" whole, and Stage A's D2, D8, D13 to D15 that it builds on.
- **The Dev Manager's reports,** whole: DM-101 (`docs/continuity/dev-manager/reviews/2026-11-26-dm-101-sv4-stage-b-brief.md`), DM-102 (`2026-11-27-dm-102-sv4-b1-c1-custody.md`) and DM-103 (`2026-11-27-dm-103-sv4-b1-pre-merge-read.md`).
- **P06.3's brief** (`docs/planning/p06-3-notifications.md`), "Outcome" and D1 to D9, and its record's "Exact-head review of P06.3".
- **The SV4 record's** "B1", "B1-C1", "Exact-head review of B1", "Exact-head review of B1-C1" (its probes P1 to P4 and reversals v1 to v9), each "Limits and deviations", and the dispositions.
- **The carried-items file's** "Carried to SV4", and its SV5 entry under "Routed by M09".
- **The code you build on,** whole:
  - `glow_domain/notifications.py` (the triggers, `DeliveryFacts`, `SessionAuthority`, `PushRequest`, the composer's `deliver`) and `notification_fixtures.py`;
  - `glow_notifications/` whole, `persistence.py` above all;
  - the models: `OutboxEvent`, `DeviceRegistration`, `NotificationSettings`, `NotificationLedgerEntry`, `PendingTokenDiscard`, `AccountSession`, `Match`, `MessageSubmission`, `ChatBinding` and the block and consent rows;
  - `glow_chat/delivery.py` whole (the pattern you follow: lease, call, receipt, `_settle`, `MAX_ATTEMPTS`, `LEASE`, `_due_ids`);
  - `glow_chat/events.py`; `glow_chat/contact.py`'s `_event`, `expire_session`, `_end_session` and `_revoke_account`; `glow_identity/revocation.py`'s `sign_out_account`;
  - `glow_discovery/interactions.py`'s `interact`;
  - the chat suite's modules, `row_locks.py` and `proofs/postgres-ordering/tests/test_chat_offline.py`;
  - the earlier tests listed below.

## 3. What to do

Build D21 to D27 and D29's B2 cases as the brief says, with D14's reversals. In particular:

1. **The triggers (D21).**
   - **The constants** live in `glow_domain/notifications.py`, the one module both writers and the deliverer may import: the schema `glow-notifications-1`, the two notification types, and the two chat session types the deliverer takes (`session_revoked`, `session_expired`) with chat's schema. A test, which may import both, pins those two values equal to `glow_chat/events.py`'s. This placement is the prompt's addition: it keeps B1's import rule and keeps `glow_chat` and `glow_discovery` free of `glow_notifications`.
   - **Each writer** creates its one event with `OutboxEvent.objects.create`, on the pattern of `glow_chat/contact.py`'s `_event` (aggregate, version, type, schema, `dedup_key`, a reference, `pending`), inside the transaction that makes the fact, and changes nothing else.
     - **`notify_match`:** the aggregate is the match, and the recipient is the like's target.
     - **`notify_message`:** the aggregate is the submission, and the recipient is the match's other member. A refused or dead-lettered message writes none.
   - **The recipient** is the account in the event's `payload_ref`, for both kinds; record it. The composer's `completed_by` is the participant who is not the recipient.
   - `activate_reciprocal` and chat's `events.DELIVERED` do not change. Chat's deliverer takes neither notification type, since it reads only its delivered types.
2. **The deliverer (D22).** It is one at a time, in process under the proof, in `glow_notifications`, and selects exactly the four types: its own two, in its schema, and chat's two session types, in chat's.
   - **Lease and check,** in one transaction: the event locked by its key and leased; the send's checks on facts read under share locks, in this order: both accounts, the match, the profiles, the consents and the block rows, then the recipient's settings and registrations. For the first delivery, the recipient's active devices are fixed as ledger rows. A refusal settles the event with no push.
   - **Call,** outside any transaction: one push per fixed device not yet recorded, through the transport's port, with the ledger key as the idempotency key. The content is P06.3's: the title `Glow`, one fixed sentence per kind, the kind and a fixed route; no identifier, name, text or count.
   - **Receipt:** each accepted send (or `repeat`) recorded in the ledger. The event is delivered when every fixed device is recorded or no longer active.
   - **Retries:** a failed call is retried with backoff, then dead-lettered after `MAX_ATTEMPTS`. A retried event's `available_at` moves by its backoff, so it holds no later event.
   - **The constants** (the prompt's additions, provisional for SV5, each recorded with its home):
     - `MAX_ATTEMPTS` 5 and the lease 30 seconds, equal to chat's, pinned equal by a test that may import both;
     - the backoff 30 seconds, doubled for each further attempt.
   - **The facts** are read with SV2's lock helpers and literal statements, as B1's adapter reads its own, never through `glow_chat`'s readers.
   - **The window** is recorded as a limit, as D22 words it, and a case shows it.
3. **`logout` (D23).**
   - For `session_revoked` and `session_expired`, the deliverer revokes every active registration that session made, as `logout`, and discards each token after the commit. A registration already revoked is no change.
   - The revocation takes the device commands' locks: the account row (`FOR NO KEY UPDATE`), then the registrations. B1's transfer relies on every writer of `DeviceRegistration` locking its account first (B1's record, "Limits and deviations").
   - A failed discard waits in `PendingTokenDiscard`, as B1's retire path does.
   - `data-model.md` ("Chat contact and the outbox") records that this deliverer is the two events' one consumer.
4. **The sweeps (D24),** one sealed entry point in `glow_notifications`, each step its own short transactions, bounded per run. One management command runs it. It is not in the runtime's command list, since the runtime installs no `glow_notifications`; a seal test proves it.
   - **The bounds** (the prompt's additions, provisional for SV5, each recorded with its home):
     - **500 rows per step per run;**
     - **a pending discard is taken once it is older than 15 minutes,** against its `created_at` (the application's clock, `timezone.now()`; B1-C1's record). That is longer than any command's run: the served runtime's worker timeout is 10 seconds, and the chat lease 30.
   - **Expired sessions:** each `AccountSession` still `valid` past its `expires_at`, found by `expires_at` and never through the actor (F-9), ordered by `expires_at` and id, is marked by `expire_session`, which writes `session_expired`. `glow_chat/contact.py` does not change.
   - **Inert registrations:** each `active` registration whose session is not current (revoked, expired, past its expiry, at a stale epoch, or of an account not `active`) is revoked as `logout`, under 3's locks, and its token discarded.
   - **The ledger's retention:** a row is removed 30 days after its event was settled (`delivered` or `dead_letter`), measured from a time the event's row already holds; record which. If the retention needs a new field, stop.
   - **The pending discards' retry,** in D24's three steps, exactly (DM-103's AO1):
     - **first,** it deletes the row by its key in its own committed transaction, which takes no account, session or registration lock. If that delete removed no row, it stops;
     - **next,** it reads the registrations, taking no lock. If one holds the reference, it stops and discards nothing;
     - **last,** it calls the store. If the discard fails, it writes the row again under a new key.
   - **The one rule** B2 keeps (D24): every transaction that writes a non-null `token_secret_ref` deletes that reference's pending discard by its key, or refuses. B2 writes no non-null `token_secret_ref`; a test shows that B1's commands are still the only writers that do.
5. **The ledger (D25):** one table for the fixed devices and the sends, as B1 made it. An event fixes at most the recipient's active registrations, which B1's bound keeps at 10.
6. **D26:** no notification kind for an unmatch or a block. A trigger whose match is not `active` is refused with the same reason whatever ended it.
7. **G-04's read (D27):** `message_recipients(sender)`, in `glow_notifications`, sealed and not served. It returns each member who received an accepted message from the sender, and whether they sent one back in that match. No new table.
8. **The code's custody words** (B1C1R-2 and B1C1R-6; DM-103's AO1 and AO2). Bring these into line with D18's and D24's words as revision 14 has them:
   - `persistence.py`'s module "Custody" paragraph (a failed re-read is a known outcome that saved nothing and leaves its handle; the sweep's three steps);
   - `_write_handle`'s docstring (an error raised after the server ran the insert can leave the row, which the immediate discard makes safe; not "nothing written");
   - `_held_since`'s last sentence;
   - `PendingTokenDiscard`'s docstring.
   - No code line in `persistence.py` changes for this item.
9. **B1C1R-3's offline check** (DM-103, item 4): a structure test that fails if `_held_since`'s failure path discards the reference (the B1-C1 review's reversal v8), with v8 as its reversal.
10. **The cases (D29, B2),** in the chat suite, each with its reversal:
    - a match notifies the earlier liker only;
    - an accepted message notifies the other member only, and a refused one notifies nobody;
    - each send check refuses: block, unmatch, pause, restriction, suspension, withdrawn consent, a setting off, no device;
    - a redelivery sends only the devices not yet recorded;
    - a sign-out, an expiry and a password change revoke the session's registrations;
    - the sweep marks a session past its expiry with no `UserSession` row;
    - a suspended account's registrations revoked by the sweep;
    - D26's sameness: a message accepted and a match made just before a block and before an unmatch, and the blocker's later unblock;
    - D27's read after an unmatch and after a block;
    - the retention;
    - a push retried with backoff holds no later event, so a logout behind it is delivered first;
    - the window as recorded: a block committed after the check and before the call does not stop that push;
    - the deliverer takes no event but its four types, and chat's deliverer takes neither notification type;
    - **carried to B2** (the carried-items file), each a case:
      - a sweep that removes a handle before its command's save, which is then refused (`token_handle_missing`);
      - a sweep that finds a registration holding the reference stops and discards nothing, and the holder's later revoke succeeds (B1-C1's record; probe P1);
      - a save that commits before the sweep's delete leaves the delete removing no row, and the sweep discards nothing (probe P3);
      - a failed discard writes the row again under a new key;
      - a settings command and a chat send of the same session, at once, both finish with no deadlock (B1's review, r19's database case).
    - **The suite's scan** holds every synthetic push token, as B1's does. A case queries the rows for each token after the deliverer and the sweeps run.
11. **The seal (D31):** `test_notifications_sealed_runtime.py`'s module list gains B2's modules, the command among them, every earlier assertion kept. A new check proves the runtime's command list holds no `glow_notifications` command. Another proves no `glow_chat` or `glow_discovery` module imports `glow_notifications`.
12. **The documentation and the CI policy:**
    - `data-model.md`: the ownership line (3), the ledger's retention and the sweeps;
    - `production-contracts.md`: "F12 on the server" gains B2's lines (who is told what, the content, the window, `logout`); its codes bullet names `token_handle_missing` among the `state_conflict` reasons (B1-C1's record);
    - the CI policy's line 13: F12's routes, B2's flows and the scanned values' push tokens and installations, in its existing form (B1's record).

**Earlier tests** (D31, PF02-R25). The manager's sweep, at this prompt's commit, read each file below. Each may change only as its entry says, every earlier assertion kept; record each, by file and test:
- **May gain B2's entry:**
  - `services/api/tests/test_notifications_sealed_runtime.py`: the module list (11);
  - `services/api/tests/test_notifications.py`: `test_the_runtime_imports_none_of_the_notification_modules`, if its prefixes need B2's modules. Its other tests keep every assertion against the fixture; `test_the_domain_module_imports_only_the_standard_library_and_its_two_neighbours` stays as it is;
  - `services/api/tests/test_notifications_routes_offline.py`:
    - `StructureTests` gains 9's check;
    - `test_no_module_imports_the_runtime_or_another_slices_routes`, and the logger loop at the end of `test_the_views_read_the_installation_from_the_header_only`, read `PACKAGE.glob("*.py")`, the top level only, and may widen to reach `management/commands/`. Their assertions stay as they are;
  - `proofs/postgres-ordering/tests/test_chat_offline.py`:
    - `ChatPlanTests.test_the_case_count_is_pinned` (37, and `PLAN`);
    - the settings test, if B2 adds a setting;
  - `row_locks.py`'s lists and `proofs/postgres-ordering/tests/test_row_locks_offline.py`, only if B2's cases lock tables they do not list.
- **Read; expected to pass unchanged** (a change to any stops you):
  - `services/api/tests/test_interactions_offline.py`:
    - `StructureTests.test_activate_reciprocal_is_called_only_from_the_like_after_its_recheck` (one statement of `interact` holds `.activate_reciprocal(`; the new event is a statement after it);
    - `test_each_command_locks_both_accounts_before_any_other_row`;
    - `test_glow_chat_imports_nothing_from_glow_discovery`;
    - `LogCaptureTests`;
    - the digest tests of `glow_chat/contact.py` (`test_every_writer_is_pinned_by_its_digest`, `test_activate_reciprocal_is_activate_match_with_one_statement_inserted` and the two `block` tests), which B2 does not reach, since `contact.py` does not change;
  - `services/api/tests/test_own_versions_offline.py`, `test_interactions_sealed_runtime.py` and `test_chat_routes_sealed_runtime.py` (`A2_MODULES` names `glow_discovery.interactions`);
  - `services/api/tests/test_match_versions_offline.py`: B2 writes no match version or contact version; if it would, stop;
  - `services/api/tests/test_model_definitions.py`:
    - its check script pins `events.DELIVERED`'s six operations, `CHAT_SCHEMA_VERSION` and `delivery.MAX_ATTEMPTS == 5`;
    - the models' count and the migration leaf (`0014_notification_devices`);
  - `services/api/tests/test_chat_adapter_offline.py`: the dead-letter checks patch `delivery`'s `ChatIdentity`, `ChatBinding`, `Match` and `MessageSubmission` and call `_plan`, never `accepted`;
  - `proofs/postgres-ordering/glow_ordering_proof/interaction_cases.py`: lines 241, 608, 833, 1022 and 2044 to 2049 count `match_activated`, `identity_created` or `contact_revoked` only;
  - `discovery_cases.py`, lines 838 to 856: every event but `preferences_changed`, around page reads that make no like;
  - `delivery_phase.py`: line 93 counts chat's delivered types; line 172 chat's schema's dead letters; lines 409 and 518 an aggregate's or two types' events;
  - `oracle.py`: reads chat's schema only;
  - `identity_support.py`'s `event_count` and `profile_cases.py`'s whole counts, in suites that make no like and no acceptance.
- **Your own sweep:** before any change, at your prompt's commit, grep every suite's source and tests and the API's tests for each thing B2 adds or changes, and record what you found. That means the two writers' functions, the outbox's counts and types, the session events, the ledger and the pending discards, the installed apps and commands, the case and plan counts, the scan's inputs, `mypy`'s list and the seal lists. A test your sweep finds is handled the same way; any other change stops you.

**Follow-ups taken if you change the file for your own work** (D30; otherwise they stay carried). Record which you took:
- **In `test_chat_offline.py`:** A2's `ChatSupportTests.test_the_text_reader_is_the_suites_one_provider`, which errors when run alone. Put the API on `sys.path` for its own duration, as B1 did for its two (B1's record, "Limits and deviations").
- **In `chat_cases.py`:** `_references_of`, unused since B1-C1, removed.
- **In the proof README:**
  - the chat suite's module-table row (line 76): F12's modules, `chat_support`'s simulations and `BeginHold`;
  - its run paragraph (line 216);
  - the chat suite's paragraph of cases, every case described.
- **In `test_row_locks_offline.py`:** A2R-13's lines 6 and 1167 ("Each of the four suites").
- The line numbers are as at this prompt's commit; read them again at yours.
- **Not B2's:**
  - A2-C1's F2 (`test_chat_routes_offline.py`), F6 (`glow_chat/contract.py`) and A2R-11 (`glow_chat/views.py`), whose files B2 does not change;
  - A2's review's limits.
  - Each stays carried, and the manager routes them at the merge receipt.

**Reversals (D14).** Every new test comes with its reversal, recorded with its failing output. At least:
- each trigger removed;
- a trigger written after its fact's transaction;
- `notify_match`'s recipient swapped to the liker;
- the deliverer taking a fifth type;
- chat's deliverer taking a notification type;
- a check read with no share lock;
- a recorded device sent again on a redelivery;
- the ledger key not passed as the idempotency key;
- a content field holding an identifier;
- the backoff removed (a logout then waits behind a retried push);
- `logout` not revoking;
- `logout` locking the registrations before the account;
- the expired sessions found through the actor;
- a step with no bound;
- the sweep discarding after a delete that removed no row;
- the sweep discarding while a registration holds the reference;
- the rewrite under the same key;
- the sweep taking a registration lock while it holds a pending row;
- a refusal reason that tells a block from an unmatch;
- G-04's read losing a recipient after an unmatch or a block;
- the retention removing an unsettled event's rows, or rows younger than 30 days;
- the runtime importing B2's modules or listing its command;
- a writer importing `glow_notifications`;
- 9's v8.

## 4. Checks, then the report

- **The trusted classifier,** from `main` (`1310896`), extracted outside your checkout and run from it with `python3 -I` and full SHAs: `python3 -I <trusted copy>/change_scope.py --base 13108961f5fb3989c72d6a9291e8a163f15a7226 --head <your code head> --merge-base` prints `"full": true` (reason `behavior-or-empty`).
- **The diff:** `git diff --name-only <START_SHA> <your head>` lists only owned paths.
- **The API's checks,** in a clean environment, after `pip install --require-hashes -r requirements-dev.lock` in `services/api`:
  - `GLOW_ENV=test python manage.py check` and `GLOW_ENV=test python manage.py test tests`;
  - `makemigrations --check --dry-run`;
  - `ruff check .` and `ruff format --check .`;
  - `mypy`, now reaching `glow_notifications`.
  - Record the counts and skips before and after.
- **The proof's offline tests,** Ruff and mypy in `proofs/postgres-ordering`, from its lock; **the contract's** `npm run check` and its Python tests, unchanged; **the mobile app's** `npm run check`, unchanged.
- **Every reversal,** with its output, each file restored (`git status` clean).
- **The run of record,** on your last code commit: every job passed, the chat job among them, within its timeout, and the gate printed "Application checks passed".

**The record,** section "B2", on B1's pattern. It holds:
- this prompt's revision and commit, and the start gate's and the environment check's results;
- what you built, by D-number, with each constant's home and value;
- your sweep, and each earlier test changed, with the entry added;
- the follow-ups taken;
- the new cases and tests, and the reversals;
- the commands and results, and any local database runs (iteration, not evidence);
- the run of record, with each job's duration;
- the threat model's inputs:
  - who is told what, and when;
  - the push's content;
  - the window D22 records;
  - a revoked or transferred device, and a session that ended;
  - the sweep's custody, and its exception (D24: a process stop between the delete and the store's answer, or a failed discard and a failed write, can leave a token in no row);
- "Substring pins, not semantics";
- every limit and deviation, among them B1R-8 as the record carries it (every register costs a `put` before its checks; rate limits on F12's routes go to P11B) and the seal test's reach (a lazy import made at request time).

Your final message, which Nathan relays:
- your branch and heads (code and records);
- the record's path;
- the run of record's link and result, with the chat job's duration;
- what you built, by D-number;
- each earlier test changed, and the follow-ups taken;
- every stop, limit and deviation, and which GitHub route you used.
