# P06.2 Stage B2 prompt — the Stream adapter, live against the development application

- **Owner:** App Manager 6. Nathan starts this session manually, in the **`Glow app`** environment (OD-36), and relays its report.
- **Revision 1, 22 October 2026.** Not for Nathan until the Dev Manager's read (DM-16) is integrated and any conditions are applied.
- **Durable brief:** [P06.2 brief](../planning/p06-2-chat-integration.md), revision 4: items 3, 4 and 6, D1 (Stage B2), D6, D8 to D10, the owned paths, "Carried to Stage B and P11" items 1 to 5, and "B2's design points" a to h.
  - Inputs: [ADR 0003](../adr/0003-chat-display-rule.md); the [chat-provider architecture document](../architecture/chat-provider-permissions.md); the P06.1 brief's "Carried to P06.2"; the [harness README](../../proofs/stream-chat/README.md); the DM-14 and DM-15 reports.
- **Where the result goes:** the session's code and tests, its section "Stage B2" in the evidence record `docs/testing/evidence/2026-10-05-p06-2-chat-integration.md`, and its update to the data model; the Foundation run on its last code commit is the run of record for the offline code; the live run is recorded from the session's own output. The manager adds its verification and updates the P11 plan's DB06 entry (its provider half).
- **Model and reasoning setting** (OD-10, OD-30, OD-33, OD-34). The reading is the recommendation; it gates nothing, and Nathan picks.
  - **TypeSafe v8.2: Fable 5.1 at max.** Effort score 3.99 (confidence 0.99); rung probabilities low 0.00, medium 0.00, high 0.00, extra high 0.01, max 0.98, ultracode 0.01. Model probabilities Fable 5.1 0.96, Opus 5.5 0.04, Sonnet 5.5 0.00, Haiku 5.5 0.00 (confidence 0.95). Twenty-four cells, computed from the two answers: Fable 5.1 at low 0.000, Fable 5.1 at medium 0.000, Fable 5.1 at high 0.000, Fable 5.1 at extra high 0.010, Fable 5.1 at max 0.941, Fable 5.1 at ultracode 0.010, Opus 5.5 at low 0.000, Opus 5.5 at medium 0.000, Opus 5.5 at high 0.000, Opus 5.5 at extra high 0.000, Opus 5.5 at max 0.039, Opus 5.5 at ultracode 0.000, Sonnet 5.5 at low 0.000, Sonnet 5.5 at medium 0.000, Sonnet 5.5 at high 0.000, Sonnet 5.5 at extra high 0.000, Sonnet 5.5 at max 0.000, Sonnet 5.5 at ultracode 0.000, Haiku 5.5 at low 0.000, Haiku 5.5 at medium 0.000, Haiku 5.5 at high 0.000, Haiku 5.5 at extra high 0.000, Haiku 5.5 at max 0.000, Haiku 5.5 at ultracode 0.000. Sent 2026-10-22T14:27:07Z. Nathan picks the cell. A revision after DM-16 is scored again.
  - **Nathan's pick:** recorded when he gives it.
- **The Dev Manager's read:** required before Nathan runs it (the charter: credential use, live provider actions and a new dependency). DM-16.
- **Environment** (OD-36): `Glow app`, which holds `STREAM_APP_ID`, `STREAM_API_KEY` and `STREAM_API_SECRET`. The session checks their names only and never prints, logs or copies their values; only the harness's credential loader reads them.
- **It runs alone** (OD-29). An exact-head review follows, then Codex's code review (its security reviews are no longer available, OD-41).
- **Deletion condition:** prune after Stage B2's PR merges and the evidence record holds the result.

**Manager:** before giving this prompt to Nathan, replace every `<START_SHA>` with the full SHA of the manager-branch commit that holds the final revision. `<WORKFLOW_LINE>` is set by DM-16: if the Dev Manager approves the timeout change (the brief, "The database job's time margin"), it reads "`.github/workflows/foundation.yml`: the `database` job's `timeout-minutes` only, from 20 to 30"; otherwise the line is removed.

---

You are the **implementation session for P06.2 Stage B2**, the live half of Stage B of P06.2, the chat integration of the Glow dating app, private repository `amthorn78/glow-dating-app`. This prompt is revision 1, from commit `<START_SHA>`.

**What exists.** Stages A and B1 merged (`main` at `3272eed`). The app has a chat contact port and its persistence adapter (`services/api/glow_chat/contact.py`), outbox delivery (`glow_chat/delivery.py`) to a chat provider port with six operations (`glow_domain/chat_provider.py`: `provision_user`, `create_channel`, `send_message`, `remove_members`, `deactivate_user`, `revoke_user_tokens`) and a fixture adapter only (`chat_provider_fixtures.py`), the token grant's transaction with its issue time from the database clock, and the race suite on a disposable PostgreSQL in CI. P06.1's harness, `proofs/stream-chat/`, proved Stream Chat's permission model against the development application 1729640 with Stream's Python server SDK `getstream` 6.1.0, with a guard, a budget, stop signals, a journal of temporary changes and cleanup. The development application is locked down (OD-37; Video and Feeds closed).

**What B2 does.** You add the Stream adapter on that port, and the signer of the client's token, and you prove both live against application 1729640 through the harness's guard. **No app runtime gains a database, real authentication or a live provider**: the adapter runs only in tests and in the harness's conformance run; P11 wires the runtime.

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
  - add a dependency anywhere but the one `getstream` pin in `services/api` (section 3, item 1).

## 1. Environment check (names only; never print values)

1. None of `DATABASE_URL`, `HD_API_KEY` or `GEO_API_KEY` may be set: `for n in DATABASE_URL HD_API_KEY GEO_API_KEY; do [ -n "${!n+x}" ] && echo "$n present"; done`. If any is present, stop and report.
2. **The three `STREAM_*` names must be present:** `compgen -e | grep -E '^STREAM_'` prints names only. Expected: `STREAM_API_KEY`, `STREAM_API_SECRET`, `STREAM_APP_ID`. If any is missing, stop and report: this session must start in `Glow app`. Never read their values yourself; the harness's credential loader does.
3. No `PG*` or `PROOF_DB_*` name should be set; report any name present, never its value.
4. The pinned toolchain is in `$HOME/.local/bin`: Node 24.19.0, npm 11.9.0 and Python 3.12.14. Put `$HOME/.local/bin` first on PATH, then record `command -v python3.12` and its version.
5. Run every command in a clean process environment, as `docs/operations/local-development.md` and the harness's README show (`env -i PATH="$PATH" HOME="$HOME" LANG=C.UTF-8`), passing the three `STREAM_*` names by reference only to the harness's live commands, and the proxy and CA variables by reference to installs.

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
- in `proofs/stream-chat/`: `glow_stream_proof/server_api.py`, `guard.py`, `credentials.py`, `usage.py`, `stops.py`, `cli.py`, `proof_run.py`'s setup and cleanup, and `client/runner.cjs`.

## 3. The work

Each item names its source in the brief. Items 1 to 6 are offline; item 7 is the only live work, and it starts only after items 1 to 6 pass offline.

1. **`getstream` 6.1.0 in the API** (design point b). Add the exact pin to `services/api/requirements.in`; regenerate `requirements.lock` and `requirements-dev.lock` with the README's `uv pip compile … --generate-hashes` commands (uv 0.12.17, Python 3.12); update `dependency-inventory.json`. Report the resolved packages that are new to the API's locks. No other dependency changes.
2. **The Stream adapter** (design points c and d). A module in `services/api` (choose its place beside the provider ports, and record why) implementing the six operations on an injected `getstream` client. It reads no environment variable and builds no client.
   - **What it sends:** provisioning upserts the user with its ID only; channel creation in `glow-match` with exactly the two members, no name, image or custom data; a message with its committed ID and text only; removal of both members; deactivation; a per-user revocation with the cut-off it is given.
   - **Outcomes:** each operation returns a `ProviderReceipt`; a repeat returns `already=True` where Stream reports the object exists. Every Stream error maps to a code in `ERROR_CODES`; no provider text is returned, stored or logged.
   - **Sealed:** extend the sealed-runtime test so that it fails if the runtime settings or URL configuration import the adapter or `getstream`.
3. **The signer** (design point e; F1 points 2 and 3; DM-15 5.2). A function that signs the client's token for a grant: `user_id`, `iat` the grant's issue time **truncated** to the whole second (never rounded), `exp` the grant's expiry, through the injected client. If `getstream` 6.1.0 cannot set `iat`, **stop before writing your own signing** and report: a hand-written JWT with the secret is a design change for the Dev Manager.
4. **One port contract, two subjects** (design point f). A contract suite that states each operation's outcomes (first call, repeat, an unknown member, channel or user) and runs offline against the fixture and against the adapter on a recorded `httpx` transport. The transport's recordings hold no credential, token or signature.
5. **The conformance command** (design point g), in the harness: `python -m glow_stream_proof conformance`, under the harness's existing preflight, guard, budget ledger, stop signals and cleanup, with the adapter built on the harness's own `ServerApi` client (`server.sdk`), so every request passes the guard. The run's IDs are the run's prefix plus `secrets.token_hex(16)`; the guard's ownership and `cleanup --apply` work unchanged. Its rows are item 7's. Offline tests for the command, with the run plan's count updated so the run still fits its budget with one rerun.
6. **Offline checks pass** (section 4, items 1 to 4) before any live command.
7. **The live run, in this order:**
   1. **`baseline`** (design point a; P06.1's carried item 1), read-only. Both differences must be 0: the chat configuration from the proof's target, and Video and Feeds from the lockdown target. If either is not 0, **stop**, record the differences, and report: P06.2 stops (ADR 0003's condition (c)).
   2. **`verify-clean`**: no proof data left from earlier runs. If anything is left, stop and report; never delete what this run did not create.
   3. **`conformance`**, once, with its rows:
      - **provisioning:** a user upserted with its ID only, read back with no name, image or custom field and role `user`; the repeat returns `already`;
      - **channel creation:** two provisioned members, read back with exactly those members and no name, image or custom data; the repeat returns `already`; a channel naming an unprovisioned member gives `member_unavailable`;
      - **send:** a message with its committed ID, read back with that ID and text; the repeat returns `already`;
      - **removal:** both members removed; the removed member's own client (the harness's runner, with a token from the signer) can no longer read the channel;
      - **deactivation:** the deactivated user's signed token is refused;
      - **token rules:** a token from the signer is accepted; a per-user revocation with a cut-off: a token whose `iat` is before it is refused, a token signed after it is accepted; the whole-second boundary (a cut-off at an exact second is sent one second later, and a token issued in that second is refused); the token's `iat` is the truncated issue time;
      - **the provider halves of F3 and CX6:** removal from a channel Stream does not have, and deactivation and revocation of a user it does not have, each give the code delivery counts as done (`channel_unavailable`, `member_unavailable`); removal from a channel whose creation succeeded at Stream works, whatever the caller saw;
      - **the contract:** the item 4 suite's outcomes, live, each compared with the fixture's; any difference is a finding, reported, not fixed silently.
   4. **`cleanup --apply`** if the run did not clean up, then **`verify-clean`**: nothing of this run remains.
   - **F3 and CX6's database half** (design point h): as DM-16 decides. Until it is applied in this prompt's final revision, the database half is not part of B2.
   - **Budget and stops:** the harness's guardrails as they are. A charge or limit signal stops the run at once, deleting nothing, and you report it; a rate limit only: wait as the README says, then one retry at most. Record the API calls the run used.

**Not in B2:** the mobile app (Stage C); any API route or served feature; the runtime's client construction or secret loading (P11); the race suite and the persistence adapter (unchanged); any configuration change at Stream.

**Rules for every change:** a test for each code change that fails without it, with its reversal made in a scratch copy outside the checkout (`git status` clean afterwards; DM-14 item 6); no weakened check, guard, deny-list or budget; no credential, token or signature in any file, log line, record or report; the harness's existing commands and their results unchanged.

**Findings outside this work:** report each with its class. Fix it here only if it could let a credential leak, let a request reach Stream outside the guard, let the adapter send a name, image or custom field, an invite, a call, a feed or an activity, or let the API runtime load the adapter.

**A departure** from any of the above that you find necessary: stop before making it and report it; it goes to the Dev Manager.

## 4. Checks

Report the exact commands and results.

1. `git diff --check <START_SHA> HEAD` and `git diff --name-only <START_SHA> HEAD`: only owned paths changed.
2. Classification with the trusted policy from `main`, outside the tree: `base=$(git rev-parse origin/main); d=$(mktemp -d); git show "$base:scripts/change_scope.py" > "$d/change_scope.py"; python3 -I "$d/change_scope.py" --base <START_SHA> --head "$(git rev-parse HEAD)" --merge-base`. Expected: full scope.
3. Hash-locked installs and `pip check` for the API and the harness; `npm ci` for the harness's client.
4. The offline checks: the API's tests (291 at the start), the harness's tests (576 at the start), Ruff, mypy, the static check with `makemigrations --check --dry-run`, the sealed-runtime test, the pin tests, the harness's `node --check` and its run-plan count.
5. **The live run:** each command's exact result line; `baseline`'s two difference counts; each conformance row's result; the API calls used; `verify-clean`'s result. No value of any `STREAM_*` variable, token or signature in what you record.
6. **The Foundation run on your last code commit:** its run ID, each job's conclusion (eight jobs), and the gate's line `Application checks passed`. Push nothing more until that run has finished (AM5-14). CI has no Stream secret; it runs the offline checks only.
7. A secret scan over your whole diff and your record.

## 5. Owned paths, push and records

- **You may change:**
  - `services/api/**`: the adapter, the signer and their tests; the sealed-runtime test; `requirements.in`, the two locks and `dependency-inventory.json`, for the `getstream` pin only. Not the runtime settings, URL configuration or configuration guards, and not `glow_chat/contact.py`, `delivery.py` or the models and migrations;
  - `proofs/stream-chat/**`: the `conformance` command, its rows, its tests, the run plan and the README. Not the guard, the deny-lists, the budget, the stop signals or cleanup's rules, and no dependency file;
  - `docs/architecture/data-model.md`, "Chat contact and the outbox": the adapter and the signer;
  - the evidence record: a new section "Stage B2" after the existing sections, which stay byte-identical.
  - `<WORKFLOW_LINE>`
- **Nothing else.** Report any other change you think is needed.
- **Commit and push** your session branch. Don't open a pull request.
- **Your section "Stage B2":** the prompt's revision and start SHA, your head, your branch and the run of record; items 1 to 7, each done (`file:line` and its test) or left (the reason), with the choices items 2 and 3 ask you to record; the new resolved packages; the live run's results, row by row; the API calls used; every check with its exact results; deviations and limits; what the exact-head review must know.

## 6. Report

Your final message is the report Nathan relays: the prompt revision (revision 1, from `<START_SHA>`); the environment check (names only); your branch, head SHA and changed paths; items 1 to 7, done or left, with the recorded choices; `baseline`'s two counts; the conformance rows' results; the API calls used; every check with its exact results, and the run of record's details; deviations, departures you stopped at, findings outside the work with their class, and limits.
