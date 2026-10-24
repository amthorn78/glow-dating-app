# P06.2 Stage B2 prompt — the Stream adapter, live against the development application

- **Owner:** App Manager 6. Nathan starts this session manually, in the **`Glow app`** environment (OD-36), and relays its report.
- **Revision 2, 23 October 2026.** Revision 1 (22 October) went to the Dev Manager; DM-16 ([report](../continuity/dev-manager/reviews/2026-10-23-dm-16-p06-2-stage-b2-prompt-read.md), `cd5b799`) approved it with conditions, which this revision applies as written, so it needs no further read (DM-03 G2). Revision 1 does not run.
- **Durable brief:** [P06.2 brief](../planning/p06-2-chat-integration.md), revision 4: items 3, 4 and 6, D1 (Stage B2), D6, D8 to D10, the owned paths, "Carried to Stage B and P11" items 1 to 5, and "B2's design points" a to h, with DM-16's conditions.
  - Inputs: [ADR 0003](../adr/0003-chat-display-rule.md); the [chat-provider architecture document](../architecture/chat-provider-permissions.md); the P06.1 brief's "Carried to P06.2"; the [harness README](../../proofs/stream-chat/README.md); the DM-14, DM-15 and DM-16 reports.
- **Where the result goes:** the session's code and tests, its section "Stage B2" in the evidence record `docs/testing/evidence/2026-10-05-p06-2-chat-integration.md`, and its update to the data model; the Foundation run on its last code commit is the run of record for the offline code; the live run is recorded from the session's own output. The manager adds its verification, the CI policy's sentence (DM-16 6.1) and the P11 plan's DB06 provider half.
- **Model and reasoning setting** (OD-10, OD-30, OD-33, OD-34, OD-42). The reading is the recommendation; it gates nothing, and Nathan picks.
  - **TypeSafe v8.2: Fable 5.1 at max.** Effort score 3.98 (confidence 0.98); rung probabilities low 0.00, medium 0.00, high 0.00, extra high 0.02, max 0.97, ultracode 0.01. Model probabilities Fable 5.1 0.96, Opus 5.5 0.04, Sonnet 5.5 0.00, Haiku 5.5 0.00 (confidence 0.95). Twenty-four cells, computed from the two answers: Fable 5.1 at low 0.000, Fable 5.1 at medium 0.000, Fable 5.1 at high 0.000, Fable 5.1 at extra high 0.019, Fable 5.1 at max 0.931, Fable 5.1 at ultracode 0.010, Opus 5.5 at low 0.000, Opus 5.5 at medium 0.000, Opus 5.5 at high 0.000, Opus 5.5 at extra high 0.001, Opus 5.5 at max 0.039, Opus 5.5 at ultracode 0.000, Sonnet 5.5 at low 0.000, Sonnet 5.5 at medium 0.000, Sonnet 5.5 at high 0.000, Sonnet 5.5 at extra high 0.000, Sonnet 5.5 at max 0.000, Sonnet 5.5 at ultracode 0.000, Haiku 5.5 at low 0.000, Haiku 5.5 at medium 0.000, Haiku 5.5 at high 0.000, Haiku 5.5 at extra high 0.000, Haiku 5.5 at max 0.000, Haiku 5.5 at ultracode 0.000. Sent 2026-10-23T13:17:21Z. Nathan picks the cell.
  - **Nathan's pick:** recorded when he gives it.
- **The Dev Manager's read:** DM-16, applied as written.
- **Environment** (OD-36): `Glow app`, which holds `STREAM_APP_ID`, `STREAM_API_KEY` and `STREAM_API_SECRET`. The session checks their names only and never prints, logs or copies their values; only the harness's credential loader reads them.
- **It runs alone** (OD-29). An exact-head review follows, then Codex's code review (its security reviews are no longer available, OD-41).
- **Deletion condition:** prune after Stage B2's PR merges and the evidence record holds the result.

**Manager:** before giving this prompt to Nathan, replace every `<START_SHA>` with the full SHA of the manager-branch commit that holds this revision.

---

You are the **implementation session for P06.2 Stage B2**, the live half of Stage B of P06.2, the chat integration of the Glow dating app, private repository `amthorn78/glow-dating-app`. This prompt is revision 2, from commit `<START_SHA>`.

**What exists.** Stages A and B1 merged (`main` at `3272eed`). The app has a chat contact port and its persistence adapter (`services/api/glow_chat/contact.py`), outbox delivery (`glow_chat/delivery.py`) to a chat provider port with six operations (`glow_domain/chat_provider.py`: `provision_user`, `create_channel`, `send_message`, `remove_members`, `deactivate_user`, `revoke_user_tokens`) and a fixture adapter only (`chat_provider_fixtures.py`), the token grant's transaction with its issue time from the database clock, `chat_tokens.revocation_cutoff_sent`, and the race suite on a disposable PostgreSQL in CI. P06.1's harness, `proofs/stream-chat/`, proved Stream Chat's permission model against the development application 1729640 with Stream's Python server SDK `getstream` 6.1.0, with a guard, a budget, stop signals, a journal of temporary changes and cleanup. The development application is locked down (OD-37; Video and Feeds closed).

**What B2 does.** You add the Stream adapter on that port, and the signer of the client's token, and you prove both live against application 1729640 through the harness's guard. **No app runtime gains a database, real authentication or a live provider**: the adapter runs only in tests and in the harness's conformance run, and `getstream` stays in the API's development scope; P11 wires the runtime.

- Nathan started you manually and will relay your report to the manager (App Manager 6). You are neither the manager nor a reviewer.
- You may use any tools, subagents, scheduled wake-ups or other capabilities the work needs.
- Your boundary is scope:
  - write only your owned paths (section 5);
  - push only your own session branch. Each push runs the Foundation workflow on your branch; read those runs if your tools can. On GitHub do nothing else: no pull request, no PR comments, no re-runs, no workflow dispatches. Change nothing in Notion.
- **Never:**
  - dump the environment, or print, echo, log, copy or commit any `STREAM_*` value, a token, a signature or a marker, in any form;
  - call any Stream application but 1729640, or any Stream product but Chat; create a call, a feed, an activity or an invite; run `configure --apply`, `restore --apply` or any command that changes the application's settings, roles, grants or channel types;
  - connect to any database, HDE, Railway or any other provider;
  - run `playwright install` or `eas`;
  - add a dependency anywhere but the `getstream` pin (and, under item 3's fallback, `pyjwt`) in `services/api/requirements-dev.in`.

## 1. Environment check (names only; never print values)

1. None of `DATABASE_URL`, `HD_API_KEY` or `GEO_API_KEY` may be set: `for n in DATABASE_URL HD_API_KEY GEO_API_KEY; do [ -n "${!n+x}" ] && echo "$n present"; done`. If any is present, stop and report.
2. **The three `STREAM_*` names must be present:** `compgen -e | grep -E '^STREAM_'` prints names only. Expected: `STREAM_API_KEY`, `STREAM_API_SECRET`, `STREAM_APP_ID`. If any is missing, stop and report: this session must start in `Glow app`. Never read their values yourself; the harness's credential loader does.
3. No `PG*` or `PROOF_DB_*` name should be set; report any name present, never its value.
4. **No `.env` file** (DM-16 1.4): `ls -a . services/api proofs/stream-chat | grep -x '\.env'` must print nothing. If one exists, report it without reading it, and stop.
5. The pinned toolchain is in `$HOME/.local/bin`: Node 24.19.0, npm 11.9.0 and Python 3.12.14. Put `$HOME/.local/bin` first on PATH, then record `command -v python3.12` and its version.
6. Run every command in a clean process environment, as `docs/operations/local-development.md` and the harness's README show (`env -i PATH="$PATH" HOME="$HOME" LANG=C.UTF-8`), passing the three `STREAM_*` names by reference only to the harness's live commands, and the proxy and CA variables by reference to installs.

## 2. Start gate

```bash
git fetch origin claude/magical-wozniak-yfmmx2 main
git merge --ff-only <START_SHA>          # on your own session branch
git rev-parse HEAD                       # must print <START_SHA>
git diff --stat <START_SHA> origin/claude/magical-wozniak-yfmmx2 -- services/ proofs/ .github/ docs/architecture/   # must print nothing
git show origin/claude/magical-wozniak-yfmmx2:docs/testing/evidence/2026-10-05-p06-2-chat-integration.md | grep -c '^## Stage B2'   # must print 0
```

If code or this stage's section has already landed on the live manager branch, this prompt is stale: stop and report (AM5-15). If any check fails, stop and report.

Then read, completely:

- root `AGENTS.md` and `CLAUDE.md`, `services/api/README.md` and `proofs/stream-chat/README.md`;
- the P06.2 brief (revision 4), whole, and the DM-14, DM-15 and DM-16 reports in `docs/continuity/dev-manager/reviews/`;
- ADR 0003 and the chat-provider architecture document, sections 3 to 8;
- the evidence record's sections "Stage B1", "Stage B1-C1" and their reviews;
- `services/api/glow_domain/chat_provider.py`, `chat_provider_fixtures.py`, `chat_tokens.py`, `services/api/glow_chat/delivery.py`, and the sealed-runtime test;
- in `proofs/stream-chat/`: `glow_stream_proof/server_api.py`, `guard.py`, `credentials.py`, `usage.py`, `stops.py`, `cli.py`, `proof_run.py`'s preflight, setup and cleanup, and `client/runner.cjs`.

## 3. The work

Each item names its source in the brief. Items 1 to 6 are offline; item 7 is the only live work, and it starts only after items 1 to 6 pass offline.

1. **`getstream` 6.1.0 in the API's development scope** (design point b; DM-16 2.1 and 2.2).
   - The exact pin goes in `services/api/requirements-dev.in`, and so into `requirements-dev.lock`, regenerated with the README's `uv pip compile … --generate-hashes` command (uv 0.12.17, Python 3.12). `requirements.in` and `requirements.lock` stay unchanged. `dependency-inventory.json` marks the new packages `"scope": "development"`, with their licences as the inventory records them. Report the resolved packages that are new to the API's development lock.
   - **A pin test** fails unless `getstream` and `httpx` (and `pyjwt`, if the signer uses it directly) have the same version and the same set of hashes in the API's development lock as in the harness's `requirements.lock`. Report any other shared package whose version differs.
   - **The SDK's environment reading** (DM-16 1.4): record, from `getstream` 6.1.0's source, whether importing `getstream` or constructing `Stream` reads the environment or a `.env` file (it brings `python-dotenv` and `pydantic-settings`).
2. **The Stream adapter** (design points c and d; DM-16 2.3, 2.4, 4.1, 4.4, 4.5). A module in `services/api` (choose its place beside the provider ports, and record why) implementing the six operations on an injected `getstream` client.
   - **The seal** (2.3, 2.4): it imports nothing from Django, `glow_persistence` or `glow_chat`, only the port, the token module and the SDK; it never calls `Stream(...)`, `Stream.from_env()` or any settings loader, reads no environment variable, and holds only the client it is given. Extend the sealed-runtime test so that it fails if the runtime settings or URL configuration import the adapter or `getstream`. The API's tests build their client with explicit dummy values under `env -i`.
   - **What it sends:** provisioning creates the user with its ID only; channel creation in `glow-match` with exactly the two members, no name, image or custom data; a message with its committed ID and text only; removal of both members; deactivation; a per-user revocation with the cut-off it is given.
   - **A repeat never undoes a revocation** (4.4): provisioning never changes an existing user (never resets fields, reactivates or clears a token cut-off); if Stream's upsert would, use a create-only path, or read first and create only when absent, and record which. Deactivation and revocation never create a user, never through an upsert. Channel creation repeated after a removal does not re-add the members; if Stream would re-add them, the adapter does not send the members on an existing channel, and you report it.
   - **The exception boundary** (4.1): the adapter maps only the SDK's own API error and `httpx`'s transport errors and timeouts to Glow codes. The harness's `GuardRefused`, `RunStopped` and `GuardrailStop`, and every other exception, propagate unchanged.
   - **Codes from status and number** (4.5): each mapping to `ERROR_CODES` is decided by HTTP status and Stream's numeric `code`; where one number covers several causes, the message's text may be tested in memory, never stored, returned or logged. A repeat returns `already=True` where Stream reports the object exists. No provider text is returned, stored or logged.
   - **No ID shape** is enforced (DM-13 2.1).
3. **The signer** (design point e; DM-16 3.1 to 3.4). A function that signs the client's token for a grant.
   - `iat` is the grant's `issued_at` truncated to the second, and never later. If Stream refuses a token whose `iat` is the current second, you may subtract a fixed number of whole seconds, never more than 5, and record which, with the live evidence.
   - `exp` is the grant's `expires_at` truncated to the second, never later, derived from the grant and not from the SDK's clock.
   - **If `getstream` 6.1.0 cannot set `iat` or `exp` from the grant, do not stop** (pre-approved, DM-16 3.3): sign the token yourself, with claims exactly `user_id`, `iat` and `exp` and the header `{"alg": "HS256", "typ": "JWT"}`; `pyjwt` at the version `getstream` resolves, added to `requirements-dev.in` as the one other pin, under item 1's pin test; the key only from the injected client's own secret or an injected signing function, never from the environment, a file or a field the adapter stores, never logged; an offline test decodes the signer's token and the SDK's token for the same user and shows the same header and claim names; a token with a wrong key fails verification; the live row shows Stream accepts it.
   - **The cut-off** (3.4): the revocation row and the adapter send `glow_domain.chat_tokens.revocation_cutoff_sent(cutoff)` as delivery gives it; neither reimplements it.
4. **One port contract, two subjects** (design point f; DM-16 4.1 to 4.3, 4.7). A contract suite that states each operation's outcomes (first call, repeat, an unknown member, channel or user) and runs offline against the fixture and against the adapter on a recorded `httpx` transport.
   - **The exception boundary's tests** (4.1): a client whose hook raises each of `GuardRefused`, `RunStopped` and `GuardrailStop`, and an unrelated `RuntimeError`, for each of the six operations; each propagates unchanged.
   - **What is sent, in code** (4.2): each operation's method, path and exact JSON keys on the recorded transport (provisioning `id` only, no `role`; creation type `glow-match`, `members` only; send the message's `id`, `text` and its sender; removal the two members; deactivation and revocation the user and the cut-off). Any `name`, `image`, `role`, custom or `data` key fails it. The recordings hold no `api_key` query parameter and no `Authorization` or `stream-auth-type` header, and a test fails if one does. Write them by hand from Stream's documented responses or P06.1's redacted results, never captured with the credentials.
   - **Every request passes the guard** (4.3): with a guard that refuses everything, each of the six operations raises `GuardRefused` before the transport sees a request.
   - **The codes the composition needs** (5.2): offline, a transport failure and a timeout give `provider_unavailable`.
   - **A send by a removed member** (4.7): the fixture gives `member_unavailable`; the suite states it, and the live row records Stream's answer.
5. **The conformance command** (design point g; DM-16 1.1, 1.3, 4.6), in the harness: `python -m glow_stream_proof conformance`, under the harness's existing preflight, guard, budget ledger, stop signals and cleanup, with the adapter built on the harness's own `ServerApi` client (`server.sdk`), so every request passes the guard.
   - **It checks the configuration itself** (1.1): before its first changing request it runs `configuration.verify` and `products.verify` on a fresh snapshot and refuses to start unless both are 0. An offline test covers each refusal.
   - **The import route** (4.6): it adds `services/api` to the import path for that command only, and imports the adapter and `glow_domain`'s port and token modules, which load without Django. A harness test shows the import in the harness's own environment.
   - **The IDs:** the run's prefix plus `secrets.token_hex(16)`, so the guard's ownership and `cleanup --apply` work unchanged.
   - Offline tests for the command, with the run plan's count updated so the run still fits its budget with one rerun.
6. **Offline checks pass** (section 4, items 1 to 4) before any live command.
7. **The live run, in this order:**
   1. **`baseline`** (design point a; P06.1's carried item 1), read-only. Both differences must be 0: the chat configuration from the proof's target, and Video and Feeds from the lockdown target. If either is not 0, **stop**, record the differences, and report: P06.2 stops (ADR 0003's condition (c)).
   2. **`verify-clean`**: no proof data left from earlier runs. If anything is left, stop and report; never delete what this run did not create.
   3. **`conformance`**, with its rows:
      - **provisioning:** a user created with its ID only, read back with no name, image or custom field and role `user`; the repeat returns `already`;
      - **re-provisioning keeps a revocation and a deactivation** (4.4): provision, revoke, provision again, and the revoked token is still refused; deactivate, provision again, and the user is still deactivated;
      - **channel creation:** two provisioned members, read back with exactly those members and no name, image or custom data; the repeat returns `already`; a channel naming an unprovisioned member gives `member_unavailable`; **creation repeated after the removal** does not re-add the members, read back;
      - **send:** a message with its committed ID, read back with that ID and text; the repeat returns `already`; **a send by a removed member, after the removal** (4.7): record Stream's answer; an acceptance is a reported difference, not a failure;
      - **removal:** both members removed; the removed member's own client (the harness's runner, with a token from the signer) can no longer read the channel;
      - **deactivation:** the deactivated user's signed token is refused;
      - **token rules:** a token from the signer is accepted; a per-user revocation with a cut-off from `revocation_cutoff_sent`: a token whose `iat` is before it is refused, a token signed after it is accepted; the whole-second boundary (a cut-off at an exact second is sent one second later, and a token issued in that second is refused); the token's `iat` and `exp` are the grant's, truncated;
      - **the provider halves of F3 and CX6** (5.2): `channel_unavailable` for removal from a channel Stream does not have; `member_unavailable` for deactivation, revocation and channel creation naming a user Stream does not have; removal from a channel whose creation succeeded at Stream works, whatever the caller saw. **A code that differs from the fixture's for any of these causes blocks B2's merge** until it is dispositioned: report it first in your report;
      - **the contract:** item 4's outcomes, live, each compared with the fixture's; any other difference is a finding, reported, not fixed silently;
      - **each mapping** to `ERROR_CODES` listed with the live row that shows it (4.5).
   4. **`cleanup --apply`** if the run did not clean up, then **`verify-clean`**: nothing of this run remains.
   5. **A closing `baseline`** (1.2): both counts 0.
   - **A rerun** (1.3): one rerun of `conformance` only when all of these hold: the first run stopped on something other than a charge or limit signal; its cleanup and `verify-clean` passed; the cause is recorded; the fix, if any, is offline and its checks pass. Otherwise, and after a second stop, stop and report.
   - **Budget and stops:** the harness's guardrails as they are. A charge or limit signal stops the run at once, deleting nothing, and you report it; a rate limit only: wait as the README says. Record the API calls the run used.
8. **The database job's timeout** (DM-16 item 6): in `.github/workflows/foundation.yml`, the `database` job's `timeout-minutes` from 20 to 30, and nothing else in the workflow. The race budgets stay unchanged. Record the database job's duration in your run of record.

**Not in B2:** the mobile app (Stage C); any API route or served feature; the runtime's client construction, secret loading or the pin's move to runtime scope (P11); the race suite, the persistence adapter and delivery (unchanged); any configuration change at Stream.

**Rules for every change:** a test for each code change that fails without it, with its reversal made in a scratch copy outside the checkout (`git status` clean afterwards; DM-14 item 6); no weakened check, guard, deny-list or budget; no credential, token or signature in any file, log line, record or report; the harness's existing commands and their results unchanged.

**Findings outside this work:** report each with its class. Fix it here only if it could let a credential leak, let a request reach Stream outside the guard, let the adapter send a name, image or custom field, an invite, a call, a feed or an activity, or let the API runtime load the adapter.

**A departure** from any of the above that you find necessary: stop before making it and report it; it goes to the Dev Manager.

## 4. Checks

Report the exact commands and results.

1. `git diff --check <START_SHA> HEAD` and `git diff --name-only <START_SHA> HEAD`: only owned paths changed.
2. Classification with the trusted policy from `main`, outside the tree: `base=$(git rev-parse origin/main); d=$(mktemp -d); git show "$base:scripts/change_scope.py" > "$d/change_scope.py"; python3 -I "$d/change_scope.py" --base <START_SHA> --head "$(git rev-parse HEAD)" --merge-base`. Expected: full scope.
3. Hash-locked installs and `pip check` for the API (runtime and development locks) and the harness; `npm ci` for the harness's client.
4. The offline checks: the API's tests (291 at the start), the harness's tests (576 at the start), Ruff, mypy, the static check with `makemigrations --check --dry-run`, the sealed-runtime test, the pin tests (the new one included), the harness's `node --check` and its run-plan count.
5. **The live run:** each command's exact result line; both `baseline` runs' two difference counts; each conformance row's result; each mapping with its row; the API calls used; `verify-clean`'s result; whether a rerun was used, and why. No value of any `STREAM_*` variable, token or signature in what you record.
6. **The Foundation run on your last code commit:** its run ID, each job's conclusion (eight jobs), the database job's duration, and the gate's line `Application checks passed`. Push nothing more until that run has finished (AM5-14). CI has no Stream secret; it runs the offline checks only.
7. A secret scan over your whole diff and your record.

## 5. Owned paths, push and records

- **You may change:**
  - `services/api/**`: the adapter, the signer and their tests; the sealed-runtime test; the new pin test; `requirements-dev.in`, `requirements-dev.lock` and `dependency-inventory.json`, for the `getstream` pin (and `pyjwt` under item 3) only. Not `requirements.in` or `requirements.lock`, the runtime settings, URL configuration or configuration guards, and not `glow_chat/contact.py`, `delivery.py` or the models and migrations;
  - `proofs/stream-chat/**`: the `conformance` command, its rows, its tests, the run plan and the README. Not the guard, the deny-lists, the budget, the stop signals or cleanup's rules, and no dependency file;
  - `.github/workflows/foundation.yml`: the `database` job's `timeout-minutes` only, from 20 to 30;
  - `docs/architecture/data-model.md`, "Chat contact and the outbox": the adapter and the signer;
  - the evidence record: a new section "Stage B2" after the existing sections, which stay byte-identical.
- **Nothing else.** Report any other change you think is needed.
- **Commit and push** your session branch. Don't open a pull request.
- **Your section "Stage B2":** the prompt's revision and start SHA, your head, your branch and the run of record; items 1 to 8, each done (`file:line` and its test) or left (the reason), with the choices items 1 to 3 ask you to record (the SDK's environment reading, the adapter's place, the provisioning path, any `iat` backdate, the signer's route); the new resolved packages; the live run's results, row by row; each mapping with its row; the API calls used; every check with its exact results; deviations and limits; what the exact-head review must know.

## 6. Report

Your final message is the report Nathan relays: the prompt revision (revision 2, from `<START_SHA>`); the environment check (names only, the `.env` check included); your branch, head SHA and changed paths; first, any code that differs from the fixture's for the causes in item 7's F3 and CX6 row; items 1 to 8, done or left, with the recorded choices; both `baseline` runs' counts; the conformance rows' results; the API calls used; every check with its exact results, and the run of record's details; deviations, departures you stopped at, findings outside the work with their class, and limits.
