# SV4 B2 exact-head review prompt — the triggers, the notification deliverer, `logout`, the sweeps and G-04's read, with a written threat model

- **Owner:** App Manager 13. Nathan starts this session manually, in the `Glow App - No Stream` environment (OD-36), and relays its report.
- **Revision 1, 27 November 2026.**
- **Durable brief:** [SV4 — the chat and notifications slice](../planning/sv4-chat-notifications.md), revision 14, its section "Stage B": "Review plan (Stage B)". That plan asks for an exact-head code and security review of each session's final code head, with a written threat model. For B2 the model covers who is told what and when, the push's content, the window D22 records, and a revoked or transferred device.
- **Where the result goes:** the report Nathan relays. The manager records it in the SV4 record, "Exact-head review of B2", with a disposition for each finding (a correction before the merge, or carried), and in the brief's "Sessions".
- **Model and reasoning setting** (OD-10, OD-30, OD-33, OD-34, OD-42). The reading is the recommendation; it gates nothing, and Nathan picks.
  - **TypeSafe v8.2: Fable 5.1 at extra high.** Effort score 3.39 (confidence 0.58); rung probabilities low 0.00, medium 0.01, high 0.17, extra high 0.26, max 0.56, ultracode 0.00. Model probabilities Fable 5.1 0.59, Opus 5.5 0.40, Sonnet 5.5 0.01, Haiku 5.5 0.00 (confidence 0.45). Twenty-four cells, computed from the two answers: Fable 5.1 at low 0.000, Fable 5.1 at medium 0.006, Fable 5.1 at high 0.100, Fable 5.1 at extra high 0.153, Fable 5.1 at max 0.330, Fable 5.1 at ultracode 0.000, Opus 5.5 at low 0.000, Opus 5.5 at medium 0.004, Opus 5.5 at high 0.068, Opus 5.5 at extra high 0.104, Opus 5.5 at max 0.224, Opus 5.5 at ultracode 0.000, Sonnet 5.5 at low 0.000, Sonnet 5.5 at medium 0.000, Sonnet 5.5 at high 0.002, Sonnet 5.5 at extra high 0.003, Sonnet 5.5 at max 0.006, Sonnet 5.5 at ultracode 0.000, Haiku 5.5 at low 0.000, Haiku 5.5 at medium 0.000, Haiku 5.5 at high 0.000, Haiku 5.5 at extra high 0.000, Haiku 5.5 at max 0.000, Haiku 5.5 at ultracode 0.000. Flags: model near tie between Fable 5.1 and Opus 5.5. Sent 2026-11-27T13:47:40Z. Nathan picks the cell.
- **The Dev Manager's read:** none before it runs. The review authorizes no credential use and no live provider action. Dev Manager 7's pre-merge read of B2 (DM-104) follows this review (D-07). It also decides D24's words, which the session's deviation extends.
- **Environment** (OD-36): `Glow App - No Stream`. No Stream variable is needed, and none may be present. `amthorn78/glow-docs` is attached, read only; this review needs nothing from it (OD-74).
- **It runs alone** (OD-29), after PR61's run and Codex's review of B2's code head and of the manager-branch commit that holds this prompt (manager workflow, step 6). It is a full review of B2's code, not a delta review.
- **Deletion condition:** prune after B2's pull request (PR61) merges and its merge receipt is recorded.

**Manager:** before giving this prompt to Nathan, replace every `<PROMPT_SHA>` with the full SHA of the manager-branch commit that holds this revision.

---

You are the **exact-head review of SV4 B2**, the server side of notifications after F12's surface (the triggers, the notification deliverer, `logout`, the sweeps and G-04's read, run in process under the proof and sealed until integration), for the Glow dating app, in the public repository `amthorn78/glow-dating-app` (public for now; OD-51). You review one exact code head in full, with a written threat model. This prompt is revision 1, from commit `<PROMPT_SHA>` of the manager branch `claude/magical-wozniak-yfmmx2`.

**What came before.**
- **SV4's brief,** revision 14 (`docs/planning/sv4-chat-notifications.md`), its section "Stage B": D21 to D27 and D29's B2 cases set B2. Much of the section is the Dev Manager's words:
  - DM-101 (`docs/continuity/dev-manager/reviews/2026-11-26-dm-101-sv4-stage-b-brief.md`) approved the design with AM1 to AM16;
  - DM-102 and DM-103 (`2026-11-27-dm-102-sv4-b1-c1-custody.md`, `2026-11-27-dm-103-sv4-b1-pre-merge-read.md`) set the token's custody. D18's custody sentences and D24's sweep are DM-103's AO1 and AO2.
- **B1** (F12's surface, with its correction B1-C1) merged with PR60 at `1310896` (`main`): the app `glow_notifications`, migration `0014`, the ORM adapter's commands with the token's custody, three sealed routes, and nineteen cases in the chat suite.
- **B2's prompt,** revision 1 (`docs/ephemeral/2026-11-27-sv4-b2-triggers-sweeps-prompt.md`), from `68a86c7`. Its additions to the brief are provisional:
  - the constants' home in `glow_domain/notifications.py`;
  - the deliverer's five attempts, 30-second lease and 30-second backoff, doubled;
  - the sweeps' 500 rows per step per run, and 15 minutes before a pending discard is taken.
- **The implementation** (branch `claude/practical-wozniak-vu08z1`; the SV4 record `docs/testing/evidence/2026-11-19-sv4-chat-notifications.md`, section "B2"):
  - code head `9dbb0c9`, run of record 45974990880: all twelve jobs passed, the chat suite 60/60;
  - records head `a9c4f3b`; no stop; 48 reversals;
  - one deviation, from the session's own review (focus item 7), and four judgments;
  - the manager verified it ("Manager verification of B2") and merged it into the manager branch at `aa11c83`. PR61 carries it into `main`.
- **Codex** reviewed `674a6bf`, PR61's first head, whose non-Markdown paths equal `9dbb0c9`: its code review completed with no findings, and PR61 has no review thread. Its review of `<PROMPT_SHA>` follows this prompt's commit, and the manager gives this prompt only after it.

**The code head under review is `9dbb0c9`.** You work at `<PROMPT_SHA>`, whose non-Markdown paths are byte-identical to `9dbb0c9` (the start gate checks this).

**Your scope:**
- **The code:** `git diff 13108961f5fb3989c72d6a9291e8a163f15a7226 9dbb0c9b863653afc4d5b32a3ab74ff712b1fc31`, its 19 non-Markdown paths, read in full at `9dbb0c9`, each changed module whole, beside its version at `1310896` where it had one:
  - **the API** (`services/api/`):
    - the new modules `glow_notifications/delivery.py`, `logout.py`, `sweeps.py`, `recipients.py` and `management/commands/notification_sweeps.py` (with the two `__init__.py` files);
    - the changed modules `glow_notifications/persistence.py`, `glow_domain/notifications.py`, `glow_chat/delivery.py` (the receipt's event), `glow_discovery/interactions.py` (the like's event), `glow_persistence/models.py` (a docstring) and `pyproject.toml` (mypy's list);
    - the tests `tests/test_notifications_delivery_offline.py`, `test_notifications_routes_offline.py` and `test_notifications_sealed_runtime.py`;
  - **the ordering proof** (`proofs/postgres-ordering/`): the chat suite's `glow_ordering_proof/chat_cases.py` and `chat_support.py`, and `tests/test_chat_offline.py`.
- **What B2 relies on unchanged,** read where it relies on it:
  - `glow_chat/contact.py`'s `_event`, `expire_session`, `_end_session` and `_revoke_account`, and `glow_chat/events.py`;
  - `glow_identity/revocation.py`'s `expire_found` and `sign_out_account`;
  - `glow_profiles/tx.py` (`lock_account`, `Tx`, `clock`, `caller_transaction_open`);
  - `glow_chat/delivery.py` whole (the pattern B2's deliverer follows, and the receipt it writes in);
  - `glow_discovery/interactions.py`'s `interact`;
  - `glow_notifications/contract.py`, `providers.py` and B1's commands in `persistence.py`;
  - `glow_domain/notification_fixtures.py` (the fixture store and transport);
  - the chat suite's `chat_settings.py`, `chat_scan.py`, `chat_suite.py` and `row_locks.py`.
- **The Markdown, as claims about the code:**
  - `docs/architecture/data-model.md` and `production-contracts.md`, their changed lines;
  - `docs/operations/ci-and-branch-policy.md`, line 13, which is governing Markdown;
  - `proofs/postgres-ordering/README.md`, its chat rows and paragraph;
  - the record's section "B2", whole, with "Manager verification of B2".
- **The runs:** 45974990880 (the run of record), and PR61's runs on `674a6bf` and on `<PROMPT_SHA>` (event `pull_request`), once they have finished; Codex's reviews of `674a6bf` and of `<PROMPT_SHA>`, and any thread on PR61.
- **Out of scope:** B1's routes and commands, which PR60's two reviews read, except where B2 calls or changes them; the real token, transport and worker (P09.2, P11B, SV5); the mobile app, which B2 does not change. Report only where B2's change affects them.

**The threat model.** Write it in your report:
- **Assets:**
  - **who is told:** a push goes only to the recipient's own active registrations, whose sessions are current, for a match still `active`, with the recipient's setting on and every send check passed. It never goes to the actor, to another account or to a device that is not the recipient's;
  - **what is told:** P06.3's content only (the title `Glow`, one fixed sentence per kind, the kind and a fixed route). No identifier, name, text or count, and nothing that tells a block from an unmatch (D26);
  - **when, and how often:** at most one push per event and installation (the ledger, D25), and none after a refusal; the window D22 records is the only gap between the check and the call;
  - **a session's end:** sign-out, expiry, a password change or reset, suspension or deletion leave no registration able to receive a push, through `logout` (D23) or the sweep (D24);
  - **the token's custody:** a reference is held only by an active registration's row, a pending discard's row and the push request handed to the transport (AM4); no row, log line, answer, exception, receipt or results file holds a token; D24's rule (every writer of a non-null `token_secret_ref` deletes its handle or refuses); the sweep's three steps and the session's deviation;
  - **the installation identifier:** a capability (AM7), never served, logged or shown. The ledger key, `<event id>:<installation id>`, is the transport's idempotency key (D22);
  - **G-04's records:** who received a member's messages and who answered, kept after an unmatch and a block, read by `message_recipients`, and served to no one;
  - **the seal:** no route, no runtime import of `glow_notifications`, no runtime command, no factory the runtime names (D16, D31);
  - **the chat job's secrets and the suite's scanned values,** which no log, results file or upload may carry.
- **Actors:**
  - a member who likes, sends, blocks, unblocks, unmatches, pauses, is restricted, suspended or deleted, withdraws a consent or turns a setting off, before the check, between the check and the call, or after the call;
  - the recipient's sessions ending in each way SV1 has, and the recipient's registrations rotated, revoked or transferred during a delivery;
  - two deliverers at once, a deliverer and a sweep, two sweeps, and a deliverer whose lease lapses;
  - the transport failing, answering `repeat`, or slow past the lease;
  - the token store failing a discard;
  - the database failing at each statement of the sweep, and a process stop between any two;
  - a store that breaks its port (AN11), as B1-C1's review's probes used it;
  - the CI runner, its logs and its artifacts;
  - a later reader of the session events (SV5) and a later writer of `DeviceRegistration` (P09.2, P11B).
- **Entry points:**
  - the two writers: `interact` and the receipt's `accepted`;
  - the deliverer's `deliver_due` and the functions it calls;
  - `logout.revoke`;
  - `sweeps.run_sweeps` and the command `notification_sweeps`;
  - `recipients.message_recipients`;
  - the chat suite's cases, support, scan and runner.

For each threat, give the code that stops it and the test or run that proves it. The focus:
1. **The triggers (D21).**
   - Each writer adds one event, in the transaction that makes its fact, and changes nothing else. The receipt's also reads the match's pair, with no lock.
   - Say whether a replayed like, a redelivered or retried receipt, or a receipt that finds its submission already `accepted` can write a second event; and whether a refused or dead-lettered message can write one.
   - Say whether the recipient in `payload_ref` is always the like's target and the match's other member.
   - Say whether `activate_reciprocal`, chat's `events.DELIVERED` and chat's deliverer are untouched in what they do. Say whether the receipt's added read can deadlock or change the receipt's outcome.
2. **Who is told (D22's check).**
   - The lease and the send's checks run in one transaction, the facts read under share locks in this order: both accounts, the match, the profiles, the consents and the block rows, then the recipient's settings and registrations.
   - Say whether any check is read without its lock or out of that order.
   - Say whether that order can deadlock with any of these: chat's send, block and unmatch; SV2's and SV3's account writers; B1's commands; `logout`; the sweeps.
   - Say whether a registration whose session is not current can be fixed or sent to, and whether the composer's checks are all reached.
3. **The call and the receipt (D22, D25).**
   - The transport is called outside any transaction, with the ledger key as its idempotency key.
   - Say whether a redelivery sends only the devices not yet recorded, whether `repeat` is recorded, and whether a lost lease or a slow transport can send twice.
   - Say whether the session's two settling judgments are right: a refusal settled as `delivered`, and an event delivered when no call of its attempt failed.
   - Say whether a retry's backoff holds no later event, as the case shows, and whether a dead-letter can leave a ledger row `pending` in a way that matters.
4. **The installation identifier and the ledger key.** The ledger key names the installation to the transport. Say:
   - whether, with the fixture transport and the seal, this is a defect at a security boundary now, or a limit for P11B (the carried entry);
   - whether any other path serves, logs or returns an installation, a reference or a token.
5. **`logout` (D23).**
   - It takes `session_revoked` and `session_expired` and revokes each active registration the session made or last rotated, under the account lock first, then the registrations by key. Each retired reference is held for its discard in the transaction and discarded after the commit.
   - Say whether it can miss a registration of the session, or revoke one it did not make, while a register, a rotate or a transfer runs at once.
   - Say whether its lock order matches B1's writers.
   - Say whether the session's limit, a `logout` that can dead-letter behind a conflicting pending row, is a defect or a limit.
6. **The sweeps (D24's first three steps, D25).**
   - Expired sessions are found by `expires_at` and marked through SV1's `expire_found` (the session's first judgment). Say whether the sweep reaching `glow_chat`'s `expire_session` through `glow_identity` keeps the purpose of B1's import rule.
   - Inert registrations are judged again under the locks. Say whether a registration made current again between the selection and the locks can be revoked.
   - The ledger's retention is measured from the event's `updated_at`. Say whether a row of an unsettled event can be removed.
   - Say whether each step's bound holds, and whether a bounded step leaves rows for the next run as it should.
7. **The pending discards' retry, and the session's deviation (D24 with AO1).**
   - The three steps: the delete by key in its own committed transaction, with no account, session or registration lock; the unlocked read of the registrations; the store's discard, and the rewrite under a new key on its failure. The bound is 15 minutes, against `created_at`.
   - **The deviation:** a failed read of the registrations writes the row again under a new key, and a failed delete leaves the row for the next run. D24's words do not cover either. The custody exception becomes "a process stop between the delete and the store's answer, or a failed read or discard and a failed rewrite, can leave a token in no row".
   - **Say:**
     - whether the deviation is safe: no discard of a reference a registration holds; no token in no row beyond the stated exception; and its effect on a holder's later retire (B1R-2's symptom);
     - whether it is the smallest safe behaviour for those two failures;
     - whether D24's words should change as the code's do. The manager puts this to Dev Manager 7 in DM-104, and your view is an input.
   - Say whether any path discards a reference whose row its own delete did not remove (B1-C1's review's probe P3).
8. **D24's one rule.** `CustodyRuleTests.test_only_b1s_register_writes_a_non_null_token_secret_ref` reads the API for writes of a non-null `token_secret_ref`. Say whether B2 writes one anywhere, and whether the test's reach (its "Substring pins, not semantics" entry) leaves a write it should see.
9. **G-04's read (D27).** Say whether `message_recipients(sender)` returns each member who received an accepted message from the sender and whether they sent one back in that match, after an unmatch and after a block. Say whether it is sealed and served to no one.
10. **The seal (D31).** `test_notifications_sealed_runtime.py` with B2's modules, and the runtime's command list. Say whether the served runtime can import B2's modules, list its command or reach a fixture. Say whether `glow_chat` and `glow_discovery` stay free of `glow_notifications`, and whether `glow_notifications` stays free of them except through `glow_identity`.
11. **The custody docstrings and the v8 check** (the prompt's items 8 and 9). Say whether the docstrings of `persistence.py`, `_write_handle`, `_held_since` and `PendingTokenDiscard` now say what the code does. Say whether `test_a_failed_re_read_discards_nothing` fails under B1-C1's review's v8, and whether `persistence.py`'s code change is only the extraction of the retire path.
12. **The cases (D29).** Check the 23 new cases against D29's B2 list and the prompt's five carried cases. Say whether any is vacuous. Say whether v40, caught offline only, is a missing test at a security boundary. Say whether B2's cases running before B1's block (the session's second judgment) weakens B1's final token check.
13. **The earlier tests and the reversals.**
    - The three changed earlier tests are `B1_MODULES`, the two widened globs and the chat plan's count. Say whether each gains only B2's entry.
    - Say whether the earlier tests the prompt lists as unchanged are unchanged.
    - Say whether any new test is vacuous, and whether the 48 reversals fail as the record says.
14. **The records.** Check every claim against the code and the runs, in:
    - `data-model.md`'s and `production-contracts.md`'s changed lines;
    - the CI policy's line 13, governing Markdown, which Dev Manager 7 reads before the merge;
    - the proof README's chat rows;
    - the record's section "B2", with "Manager verification of B2".
    - Say whether the stale line the session routed (`providers.py`, line 44) is more than a stale line.

**Re-run, at least,** in a scratch copy of `9dbb0c9`, each package in a virtual environment installed from its own lock with `pip install --require-hashes`, under `env -i`:
- **The API:** `GLOW_ENV=test python manage.py check && GLOW_ENV=test python manage.py test tests`; `ruff check .`, `ruff format --check .` and `mypy`; `GLOW_ENV=test python manage.py makemigrations --check --dry-run`.
- **The ordering proof:** its offline tests, `ruff` and `mypy`.
- **Reversals, offline, on copies,** each restored afterwards. For each, say which test fails, or that only a database case catches it:
  - `notify_match`'s recipient swapped to the liker;
  - a trigger written after its transaction commits;
  - the deliverer taking a fifth event type;
  - a check read with no share lock;
  - the ledger key not passed to the transport;
  - the backoff removed;
  - `logout` locking the registrations before the account;
  - the sweep discarding after a delete that removed no row;
  - the sweep discarding after a failed read of the registrations;
  - the runtime listing `notification_sweeps`;
  - any other you doubt.
- **The database cases, informational:** the chat suite on a throwaway PostgreSQL under P06.DB's D4, if Docker allows, with any probe you need. Useful probes: a block between the check and the call; a lease that lapses mid-call; a sweep racing a register's save; a failed read in the sweep's second step.

**What comes after this review: the correction classes** (D-07; the manager workflow, step 6). Report every finding with its severity. A correction pass takes every blocking finding, and any should-fix finding that is:
- **a defect in application behaviour:**
  - a push sent twice for one event and installation, or none where every check passes;
  - an event written twice, or not at all, for its fact;
  - a session's end that leaves a registration able to receive a push;
  - a sweep that marks, revokes or removes the wrong rows, or passes its bound;
  - a deadlock or a crossing;
- **a defect at a security boundary:**
  - a push to anyone but the recipient's own current registrations, or for a match not `active`, or against a refused check;
  - content beyond P06.3's, or a notification that tells a block from an unmatch;
  - a token or a reference anywhere AM4 does not allow, a reference discarded while a registration holds it, or a custody rule left open;
  - an installation identifier served or logged;
  - a seal crossed; HDE's boundary crossed;
- **a false claim that a decision or the merge would rest on** (D-07): where that claim is what a decision, an acceptance check or the merge reads.

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
  - GitHub, read only, to read the runs, PR61 and Codex's reviews.

  A page you cannot reach is named as unread, never filled from memory.
- **Local database runs** are allowed only as P06.DB's D4 allows them (`docs/planning/p06-db-disposable-postgres-proof.md`, D4, its four conditions):
  - a throwaway PostgreSQL in Docker, from that image, on loopback only;
  - a generated password, and the run's marker on each database;
  - none of `DATABASE_URL`, `HD_API_KEY`, `GEO_API_KEY` or any `PG*` name present;
  - removed afterwards.
  - Migrations reach that database only through the proof's own commands; never run `manage.py migrate` yourself.
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
git merge-base --all origin/main HEAD                 # expected: one line, 13108961f5fb3989c72d6a9291e8a163f15a7226
git merge-base --is-ancestor <PROMPT_SHA> origin/claude/magical-wozniak-yfmmx2 && echo "this prompt's commit is on the live branch"
git diff --quiet 9dbb0c9b863653afc4d5b32a3ab74ff712b1fc31 HEAD -- . ':!*.md' && echo "the code head under review"
git diff --quiet 9dbb0c9b863653afc4d5b32a3ab74ff712b1fc31 origin/claude/magical-wozniak-yfmmx2 -- . ':!*.md' && echo "no code on the live branch after 9dbb0c9"
git show origin/claude/magical-wozniak-yfmmx2:docs/testing/evidence/2026-11-19-sv4-chat-notifications.md | grep -c -E '^#+ Exact-head review of B2'   # must print 0
```

If any check fails, stop and report. The prompt is stale if its commit is not on the live branch, a non-Markdown path changed there after `9dbb0c9`, or this review is already recorded.

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
- the brief, revision 14: the section "Stage B" whole, and Stage A's D2, D8 and D13 to D15 it builds on;
- DM-101's, DM-102's and DM-103's reports, whole;
- P06.3's brief (`docs/planning/p06-3-notifications.md`), "Outcome" and D1 to D9;
- B2's prompt, its stop rule, "What to do" and "Earlier tests" above all;
- the record's sections "B1-C1" and "Exact-head review of B1-C1" (its probes P1 to P4 and reversals v1 to v9), and the section "B2", whole, with "Manager verification of B2";
- the carried-items file's "Carried to SV4";
- every file in the code diff, whole, beside its version at `1310896`.

**The runs,** read from GitHub:
- 45974990880, and PR61's runs on `674a6bf` and on `<PROMPT_SHA>` if they have finished: every job's conclusion and duration, and the gate's line;
- Codex's reviews of `674a6bf` and of `<PROMPT_SHA>`, and any thread on PR61.

## 3. What to do

1. Write the threat model, then review the change against the focus, item by item.
2. In a scratch copy of `9dbb0c9`: re-run the checks and the reversals above, and any you doubt; run the database cases locally under D4 if you can, informational.
3. For each finding: its severity (blocking, should fix, nit), its file and line, the evidence, and whether it falls in a correction class.

## 4. Report

Your final message is the report Nathan relays:
- the prompt revision (revision 1, from `<PROMPT_SHA>`), and the start gate's, the classification's and the environment check's results;
- the threat model, each threat with its stopping code and its test or run;
- the focus, item by item, with your verdict on each, focus item 7's view on D24's words among them;
- every finding, with its severity, file and line, evidence and correction class;
- the checks and reversals you re-ran, each with its exact result, and any local run;
- the runs and Codex's reviews as you read them, and which GitHub route you used;
- your verdict: **approve**, **approve with nits** or **changes requested**;
- what you did not read or run, and why.
