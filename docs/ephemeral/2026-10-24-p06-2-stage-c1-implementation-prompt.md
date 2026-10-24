# P06.2 Stage C1 prompt — the history read, the conversation reads and the contracts, offline

- **Owner:** App Manager 7. Nathan starts this session manually, in the `Glow App - No Stream` environment (OD-36), and relays its report.
- **Revision 1, 24 October 2026.** It goes to the Dev Manager with the brief's revision 12 (DM-22) and does not run before that read.
- **Durable brief:** [P06.2 brief](../planning/p06-2-chat-integration.md), revision 12: "Stage C under OD-45", points a to k; D5, D6 and D8; item 5; Stage C1's owned paths; acceptance check 6.
  - Inputs:
    - the brief's "The client-token question (D8)", with Nathan's answer (OD-45);
    - [ADR 0003](../adr/0003-chat-display-rule.md);
    - the evidence record's sections for Stages A, B1 and B2;
    - the [DM-20](../continuity/dev-manager/reviews/2026-10-23-dm-20-p06-2-b2-live-rows-and-d8.md) and [DM-21](../continuity/dev-manager/reviews/2026-10-24-dm-21-p06-2-od-45-governing-read.md) reports, and DM-22's when it is written.
- **Where the result goes:**
  - the session's code and tests, and its section "Stage C1" in the evidence record `docs/testing/evidence/2026-10-05-p06-2-chat-integration.md`;
  - its updates to the production contracts and the data model.

  The Foundation run on its last code commit is the run of record. The manager adds its verification and records the outcome in the brief's "Sessions".
- **Model and reasoning setting** (OD-10, OD-30, OD-33, OD-34, OD-42). The reading is the recommendation; it gates nothing, and Nathan picks.
  - **TypeSafe v8.2: Opus 5.5 at extra high.** Effort score 2.92 (confidence 0.77); rung probabilities low 0.00, medium 0.02, high 0.17, extra high 0.66, max 0.14, ultracode 0.00. Model probabilities Fable 5.1 0.10, Opus 5.5 0.86, Sonnet 5.5 0.04, Haiku 5.5 0.00 (confidence 0.81). Twenty-four cells, computed from the two answers: Fable 5.1 at low 0.000, Fable 5.1 at medium 0.002, Fable 5.1 at high 0.017, Fable 5.1 at extra high 0.066, Fable 5.1 at max 0.014, Fable 5.1 at ultracode 0.000, Opus 5.5 at low 0.000, Opus 5.5 at medium 0.017, Opus 5.5 at high 0.146, Opus 5.5 at extra high 0.568, Opus 5.5 at max 0.120, Opus 5.5 at ultracode 0.000, Sonnet 5.5 at low 0.000, Sonnet 5.5 at medium 0.001, Sonnet 5.5 at high 0.007, Sonnet 5.5 at extra high 0.026, Sonnet 5.5 at max 0.006, Sonnet 5.5 at ultracode 0.000, Haiku 5.5 at low 0.000, Haiku 5.5 at medium 0.000, Haiku 5.5 at high 0.000, Haiku 5.5 at extra high 0.000, Haiku 5.5 at max 0.000, Haiku 5.5 at ultracode 0.000. Sent 2026-10-24T03:35:25Z. Nathan picks the cell.
  - **Nathan's pick:** recorded when he gives it.
- **The Dev Manager's read:** DM-22 reads this revision with the brief's revision 12 before Nathan runs it. If DM-22 sets conditions, revision 2 applies them as written and needs no further read (DM-03 G2).
- **Environment** (OD-36): `Glow App - No Stream`. No Stream variable is needed, and the session calls no provider.
- **It runs alone** (OD-29). Its exact-head review follows, then Codex's code review of the final head (OD-41).
- **Deletion condition:** prune after Stage C1's PR merges and the evidence record holds the result.

**Manager:** before giving this prompt to Nathan, replace every `<START_SHA>` with the full SHA of the manager-branch commit that holds this prompt's final revision.

---

You are the **implementation session for P06.2 Stage C1**. C1 is the first part of Stage C of P06.2, the chat integration of the Glow dating app, in the private repository `amthorn78/glow-dating-app`. This prompt is revision 1, from commit `<START_SHA>`.

**What exists.** Stages A, B1 and B2 are merged; B2 merged on 24 October as PR31, at `3572c41`.

- **The contact port and its persistence adapter:** `services/api/glow_domain/chat.py` and `services/api/glow_chat/contact.py`. They carry P06.DB's transaction design:
  - `READ COMMITTED`;
  - row locks in one order;
  - every check made on the locked rows;
  - the time read from `clock_timestamp()` after the locks.
- **B1's token grant** reads its rows under shared locks and writes nothing.
- **The outbox delivers to the chat provider port** (`services/api/glow_domain/chat_provider.py`). The port has six operations:
  - a fixture adapter, `chat_provider_fixtures.py`;
  - the Stream adapter on `getstream` 6.1.0, `chat_provider_stream.py`, which B2 proved live.
- **The race suite** (`proofs/postgres-ordering/`) runs the reference design and the app's adapter in the Foundation job "Database proof checks".
- **The production contracts** are in `packages/contracts/production/`, with generated TypeScript and validators in `apps/mobile/src/contracts/generated/`.
- **Nothing is served.** The API runtime imports none of the chat code, and no app runtime has a database, real authentication or a live provider.

**Why C1 exists.** On 24 October Nathan decided D8 as option (b) (OD-45): *"b, and I do think the stream architecture is still better than building our own, but I don't want features "snuck" in for sure"*.

- The app holds no Stream credential.
- Glow's API serves history and new messages.
- Stream stays the provider behind Glow's server.

C1 builds the server half of that, offline, with the contracts the app will be held to. C2, a later session, builds the mobile interface on them.

**How you work:**
- Nathan started you manually and will relay your report to the manager (App Manager 7). You are neither the manager nor a reviewer.
- You may use any tools, subagents, scheduled wake-ups or other capabilities the work needs.
- Your boundary is scope:
  - write only your owned paths (section 5);
  - push only your own session branch. If your branch is under the workflow's push filter (`claude/**`), each push runs the Foundation workflow on it; read those runs if your tools can. On GitHub do nothing else: no pull request, no PR comments, no re-runs, no workflow dispatches. Change nothing in Notion.
- **Never:**
  - dump the environment, or print, echo, log, copy or commit any credential, token, password or marker, in any form;
  - call Stream, or run any harness command in `proofs/stream-chat/` that sends a request;
  - connect to any database except a disposable one that you or the job start for this proof (P06.DB brief, D4), or set a comment on any other database. Never connect to HDE, Railway or any other provider;
  - run `playwright install` or `eas`;
  - run Django's `migrate` anywhere except against a disposable proof database, from the proof's own settings;
  - add or change a dependency, a version or a lock file, in any component.

## 1. Environment check (names only; never print values)

1. None of `DATABASE_URL`, `HD_API_KEY` or `GEO_API_KEY` may be set: `for n in DATABASE_URL HD_API_KEY GEO_API_KEY; do [ -n "${!n+x}" ] && echo "$n present"; done`. If any is present, stop and report.
2. **No `STREAM_*` name may be set:** `compgen -e | grep -E '^STREAM_'` prints names only. If any is present, stop and report: this session must start in `Glow App - No Stream`.
3. No `PG*` or `PROOF_DB_*` name should be set (`compgen -e | grep -E '^(PG|PROOF_DB_)'`). If one is present, report its name first, never read or use its value, and run every proof command in a clean process environment that lacks it.
4. **No `.env` file:** `ls -a . services/api proofs/postgres-ordering packages/contracts apps/mobile | grep -x '\.env'` must print nothing. If one exists, report it without reading it, and stop.
5. **The toolchain:** the pinned toolchain is in `$HOME/.local/bin`: Python 3.12.14, Node 24.19.0 and npm 11.9.0.
   - Put `$HOME/.local/bin` first on PATH in every process you run, then record `command -v python3.12` and its version.
   - Create any virtual environment with `python3.12`, outside the checkout.
6. **A clean process environment.** Run the API's, the proof's, the contracts' and the mobile app's commands in a clean process environment, as `docs/operations/local-development.md` and each README show: `env -i PATH="$PATH" HOME="$HOME" LANG=C.UTF-8`, plus only the component's own variables. Installs get the proxy and CA variables by reference, never printed.
7. **What a local database can use** (P06.DB brief, D4). Record whether `docker info` succeeds (its exit status only), and the output of `command -v initdb pg_ctl postgres pg_isready psql`.

## 2. Start gate

```bash
git fetch origin claude/magical-wozniak-yfmmx2 main
git merge --ff-only <START_SHA>          # on your own session branch
git rev-parse HEAD                       # must print <START_SHA>
git diff --stat <START_SHA> origin/claude/magical-wozniak-yfmmx2 -- services/ proofs/ packages/ apps/ .github/ docs/architecture/   # must print nothing
git show origin/claude/magical-wozniak-yfmmx2:docs/testing/evidence/2026-10-05-p06-2-chat-integration.md | grep -c '^## Stage C1'   # must print 0
```

- The fourth and fifth commands check the live manager branch. If code or this stage's section has already landed there, this prompt is stale: stop and report (the manager workflow, step 3, AM5-15).
- If any check fails, stop and report.

Then read, completely:

- root `AGENTS.md` and `CLAUDE.md`;
- `services/api/README.md`, `proofs/postgres-ordering/README.md`, `packages/contracts/README.md`, and `apps/mobile/AGENTS.md` (you change only its generated contracts);
- the P06.2 brief, `docs/planning/p06-2-chat-integration.md`, revision 12: "What P06.2 delivers", D1 to D8, the owned paths, "The client-token question (D8)" and "Stage C under OD-45";
- ADR 0003, `docs/adr/0003-chat-display-rule.md`;
- the DM-20 and DM-21 reports, and DM-22's (`docs/continuity/dev-manager/reviews/`);
- the P06.2 evidence record, Stage A's, B1's and B2's sections and their reviews;
- `docs/architecture/data-model.md`, "Chat contact and the outbox", and `docs/architecture/production-contracts.md`, F09 to F13;
- `services/api/glow_chat/`, `services/api/glow_domain/chat*.py`, `services/api/glow_persistence/models.py`, and their tests;
- `proofs/postgres-ordering/` whole;
- `packages/contracts/` whole, and `apps/mobile/src/contracts/`;
- `.github/workflows/foundation.yml`: the `mobile`, `smoke` and `database` jobs, and the gate.

## 3. The work

Each item names its design point in "Stage C under OD-45". Where DM-22 sets a condition, it is quoted in this prompt's revision 2. Meet it as written.

**The provider port** (point b)

1. **The text read: one new port operation.** The operation takes a channel ID and a page's message IDs, and returns, for each message the provider holds, its ID and text, and nothing else.
   - **The operation.** Name it and add it to `OPERATIONS` with its arguments.
   - **A cap in code.** Fix the page's largest size in code; it must not exceed the production page limit of 50. Record the value.
   - **The fixture adapter** answers from the messages it was sent. A test can plant a message the fixture holds that Glow never sent.
   - **The Stream adapter** calls `get_many_messages` (`getstream` 6.1.0):
     - never with `member_custom_include`;
     - reads only each returned message's ID and text;
     - drops every other field, and every message it did not ask for;
     - maps every error to a Glow code, as B2's operations do. No provider text is stored, logged or returned.
   - **The adapter's tests,** offline, with the SDK faked as B2's tests fake it:
     - the request's exact shape, with no `member_custom_include`;
     - a response carrying extra fields (`user`, `member`, custom data, reactions, attachments, a `type` other than `regular`) and an extra message, of which only the asked-for IDs and texts survive;
     - each error class mapped to its code.
   - **Unchanged:** the port's six existing operations and B2's adapter code for them.
   - **No live row in C1.** The live row runs in P11's next live conformance run (point i).

**The persistence adapter** (points b, c and e)

2. **The history read.** The adapter returns a page of a conversation for a member's session.
   - **Glow's rows.** The page is made of the match's accepted `MessageSubmission` rows, in a deterministic order from Glow's rows. Name the columns and record why.
   - **Older and newer pages** by an opaque cursor; the cursor is never a provider ID.
   - **The member's own pending and failed submissions** appear only to that member, with their state. A pending one carries its spool text to its sender only. The other member's pending and failed submissions never appear.
   - **The texts** of the page's accepted messages come from item 1's operation, in one call. A message the provider does not return is in Glow's "unavailable" state and counted for reconciliation, never with provider text.
   - **A page with no accepted message makes no provider call.** "Anything new?" is answered from Glow's rows.
3. **The checks, before and after the provider call** (point c).
   - **Before the provider call:** the read makes the send's checks on rows read under the send's shared locks, as B1's grant does. They are:
     - a valid, current session of an `active` account;
     - the match active, with no block either way;
     - neither member suspended or deleted;
     - neither profile paused or restricted;
     - both onboarding consents accepted.

     A refused read makes no provider call.
   - **After the provider call:** the read checks again, in a new statement that sees every revocation committed before it, and returns the page only if that check passes too.
   - **The refusal is a Glow code.** Tell a member nothing about why the conversation ended beyond what the match's projection shows (F10, F13).
   - **The order is fixed.** Never return a page whose final check ran before the provider call.
4. **The conversation list.** It returns, for each of the member's conversations:
   - the match;
   - Glow's state;
   - the unread count, from Glow's accepted rows after the member's `ChatReadCursor`;
   - a marker of its latest message.

   It makes item 3's checks for the session, applies the per-match checks to each conversation, and calls no provider. A conversation the member may no longer see is not listed.
5. **The read cursor** (point e). A command moves the member's own `ChatReadCursor` to an accepted message of that match.
   - It moves only forward, and only for a member who passes item 3's checks.
   - It is idempotent, so a repeat changes nothing.
   - The other member's cursor is never returned.
6. **No migration and no data-model change** (point b). If you find that one is necessary, stop before making it, record why, and report it: it is a departure.

**The suite** (point c)

7. **Forced cases on the adapter's subject, for the history read.** Run one pair for each revocation: block, unmatch, suspension, deletion, sign-out, session expiry, pause, restriction and consent withdrawal.
   - **Committed while the read waits** between its provider call and its final check: the read is refused.
   - **Committed after the final check:** the read returns its page.
   - **Each forced wait is observed,** as for the send. The fixture provider makes the provider call; a probe hold point between the call and the final check makes the wait.
   - Add an oracle rule only if you can state one that the database's records decide. Any rule you add comes with a planted control that fails in the same run.
   - **Unchanged:** `reference.py` is byte-identical to `3572c41`, and its 56 cases and ten controls are unchanged. Show the hash or an empty diff.
   - **The job's time.** The job's timeout stays 30 minutes, and both subjects keep their stress budgets. If a measured run shows the job no longer fits, report the numbers. Do not raise the timeout or shrink a run.

**The contracts** (point f)

8. **New production DTOs** in `packages/contracts/production/gapp-api-v1.schema.json`, with the flow registry's entries (`flows-v1.json`) and `openapi.json` where the package keeps them in step:
   - **the conversation list:** for each conversation, the match ID, Glow's state, the unread count and its latest message's marker;
   - **a page of messages:** for each message, Glow's submission ID, own or other, Glow's time, the text or the "unavailable" state, and for own messages the delivery state; and the page's cursors;
   - **the page request** for one conversation;
   - **the read-cursor command.**

   Reuse the package's existing definitions (`Identifier`, `Instant`, `CommandMeta`, `AppResponse`, `Error`) wherever they fit. A state that tells a member why contact ended must not be added.
9. **`ChannelEntitlement` loses `channel_ref`** (DM-21 2.3).
   - Remove it, with its conditional, from the DTO, the corpus and every consumer.
   - Record that the provider's channel ID no longer reaches the client.
10. **The shared corpus** (`corpus/shared-v1.json`) gets a case for each new DTO's valid form. It also gets a rejection for each provider field, run through Python and the generated validators:
    - a provider user, channel or message ID (`provider_message_ref`, `channel_ref`, `cid`, `user_id`);
    - a `user` or `member` object, or `custom` data;
    - a provider timestamp field;
    - an event type such as `member.updated` or `ai_indicator.update`;
    - an error text.
11. **Regenerate** the generated outputs with `npm run generate --prefix packages/contracts`, never by hand. The mobile app's checks must still pass with them.
12. **The server's projections.** Write functions that turn items 2, 4 and 5's results into these DTOs. Their tests validate every output against the schema, and show that no provider ID or provider field can reach one. Serve no endpoint: P11 does.

**The documents**

13. Update:
    - `docs/architecture/production-contracts.md`: F11's row and notes, with the new DTOs, OD-45 ("no provider token is issued") and `channel_ref`'s removal;
    - `docs/architecture/data-model.md`, "Chat contact and the outbox": the history read, its two checks, the conversation list and the cursor command, and which rows each reads;
    - the contracts README, if a command or a scope sentence changes.

**Not in C1:**
- the mobile screens (C2);
- any API route, URL or served feature;
- a WebSocket or any realtime service;
- push (P06.3);
- removing the dormant token code (point h);
- any live call;
- any dependency.

**Rules for every change:**

- **A test for each change.** Each code item gets a test that fails without the change and passes with it. Say which test covers which item.
- **Reversals in a scratch copy, never the checkout.** Make each fix reversal in a copy outside the repository, with absolute paths. Confirm afterwards that `git status` is clean.
- **Evidence comes from the database.** The suite judges every ordering guarantee by what PostgreSQL recorded, never by what the test code believes it did.
- **No weakened check.** Never loosen a case, the oracle, a control's signal, a floor or a corpus rule to make a run pass. A flaky case is a finding (OD-21), not a retry.
- **No password or marker anywhere:** not in the diff, a log line, the evidence record or your report.
- **No dependency change** in any component: the `requirements*` and lock files, the dependency lists in `pyproject.toml`, `package.json`, `package-lock.json` and `dependency-inventory.json` all stay unchanged.

**Findings outside this work:** report each with its class. Fix one here only if it could do one of the following, and then with a test:

- let a send or a read succeed after a revocation that invalidates it, without the suite failing;
- let a provider ID, provider field or provider text reach a DTO, a stored row, a log or a user;
- let a password, the marker or a connection value reach a log, an artifact or a file outside the job's temporary directory;
- let the job, the proof or the adapter connect to anything other than its own disposable database, or let the API runtime load the chat code or connect to any database;
- let the provider receive a name, image or custom field, an invite, a call, a feed or an activity.

**A departure** from any point above that you find necessary: stop before making it, record it and the reason, and report it. It goes back to the Dev Manager (DM-15 1.3).

**Local runs** (P06.DB brief, D4). Use a disposable database in your own sandbox:
- with `docker run` and the job's recipe, if Docker works;
- otherwise a throwaway cluster from local binaries;
- otherwise CI.

The same rules hold: a generated password and a new marker, loopback or a socket only, the database removed afterwards, and no forbidden or `PG*` name present. Local runs are iteration, not evidence. Your report says which you used.

## 4. Checks

Report the exact commands and results.

1. **The diff:** `git diff --check <START_SHA> HEAD`, and `git diff --name-only <START_SHA> HEAD`. Only owned paths changed.
2. **Classification** with the trusted policy from `main`, run outside the tree, as root `AGENTS.md` requires. Expected: full scope.

   ```bash
   base=$(git rev-parse origin/main); policy_dir=$(mktemp -d)
   git show "$base:scripts/change_scope.py" > "$policy_dir/change_scope.py"
   python3 -I "$policy_dir/change_scope.py" --base <START_SHA> --head "$(git rev-parse HEAD)" --merge-base
   ```

3. **The installs** from the locks, in a clean process: `pip install --require-hashes` and `pip check` for the API and the proof; `npm ci --ignore-scripts` for the contracts and the mobile app.
4. **The offline checks,** with each component's documented commands. Give counts at the start and at your head.
   - **The API:** the unit tests, Ruff check and format, mypy with its file count, the Django pin test, the toolchain pin test, the static model check with `makemigrations --check --dry-run`, and the sealed-runtime test.
   - **The proof:** its unit tests, Ruff and mypy.
   - **The contracts:** `npm run generate` (no diff after), `npm run check`, and the Python contract tests (`packages/contracts/tests`).
   - **The mobile app:** `npm run check`.
5. **The dependency files are unchanged:** an empty `git diff <START_SHA> HEAD` over every dependency file named in section 3. Also show that `reference.py` and migrations `0001` to `0003` are unchanged, by their hashes or by an empty diff.
6. **Your local runs, if any:** which database, its version, and the results, marked "iteration, not evidence".
7. **The Foundation run on your last code commit:** its run ID, each job's conclusion (eight jobs), and the gate's log line, which must be `Application checks passed`.
   - **Wait before pushing again.** After pushing your last code commit, push nothing more to your branch until that commit's Foundation run has finished. Runs of the same branch cancel each other (the CI policy), so an early records push can cancel the code run (AM5-14).
   - A push that changes only Markdown skips the application jobs. If your last commit changes only the record, the run of record is the push run of your last code commit, and your record says so.
   - **From the database job's log, per subject:**
     - the refusals;
     - each case with its observed waits, item 7's cases named;
     - the oracle's result over every row;
     - each race's iterations, overlaps and count per commit order;
     - each control's declared signal and whether it was met;
     - the job's time against its timeout.
   - **From the mobile job's log:** the generation check and the corpus run.
   - **Confirm that the log shows no password and no marker,** and no `***` mask where either would be. If your tools cannot read the run, say so; re-run or dispatch nothing.
8. **A secret scan over your whole diff:** no secret, token, API key, password, marker value or email address.

## 5. Owned paths, push and records

- **You may change:**
  - `services/api/**`, except:
    - its dependency files (`requirements*.in`, `requirements*.lock`, the dependency lists in `pyproject.toml`, `dependency-inventory.json`);
    - its migrations;
    - its runtime settings, URL configuration and configuration guards (`glow_api/settings.py`, `glow_api/urls.py`, `glow_api/configuration*.py`, `glow_api/runtime.py`);
  - `proofs/postgres-ordering/**`, except its dependency files and `glow_ordering_proof/reference.py`;
  - `packages/contracts/**`, except its dependency files;
  - `apps/mobile/src/contracts/generated/**`, only as `npm run generate` writes it, and the mobile app's existing tests or code only where `channel_ref`'s removal requires it (report each such change);
  - `docs/architecture/production-contracts.md` and `docs/architecture/data-model.md`;
  - the evidence record `docs/testing/evidence/2026-10-05-p06-2-chat-integration.md`: a new section "Stage C1" only, after the existing sections, which stay byte-identical.
- **Nothing else.** That includes the briefs, the CI policy, the P11 acceptance plan, `.github/`, `proofs/stream-chat/`, the rest of `apps/`, `scripts/`, any `.claude/` path and every other document. Report any other change you think is needed.
- **Commit and push** your session branch. Don't open a pull request.
- **Your section "Stage C1"** in the evidence record:
  - the prompt's revision and start SHA, your head, your branch and the run of record;
  - for items 1 to 13 of section 3: done (`file:line` and its test) or left (the reason), with the choices items 1 and 2 ask you to record;
  - the run of record's results per subject, against the last run on `main`'s code, PR31's run 40057495942;
  - local runs, marked "iteration, not evidence";
  - every check, with its exact results;
  - deviations and limits;
  - what the exact-head review must know.

## 6. Report

Your final message is the report Nathan relays:

- the prompt revision you received, and the commit it came from;
- the environment check, and what a local database could use;
- your branch, head SHA and tree, and the changed paths;
- for items 1 to 13 of section 3: done or left, with the recorded choices;
- every check, with its exact results, and the run of record's details from section 4 item 7;
- which local database you used, if any;
- deviations, departures you stopped at, findings outside the work with their class, open questions and limits.
