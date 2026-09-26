# P06.1 Stream Chat permission proof

A sandbox harness that proves, against Nathan's development Stream application 1729640 and with synthetic users only, whether Stream Chat's permission model supports Glow's chat design:

- the app server controls channel membership and authorizes every send;
- a client never sends through Stream directly, because the app server sends on the user's behalf after its match and block check;
- a client's token lets it read its own current match's channel and nothing else.

Brief: [P06.1](../../docs/planning/p06-1-chat-provider-proof.md). Evidence: [2026-09-25 P06.1 evidence](../../docs/testing/evidence/2026-09-25-p06-1-chat-provider-proof.md).

This is proof tooling, not application code. It is outside the application runtime, and it sets no `GLOW_*` variable. It never touches a database, HDE or Railway.

## Layout

| Path | What it is |
|---|---|
| `glow_stream_proof/` | Server side (Python, Stream's server SDK `getstream`): configuration, the app-side send path, the bypass matrix, orchestration, usage guardrails, redaction |
| `client/runner.cjs` | Client side (Node, Stream's client SDK `stream-chat`): one process per client session, driven over stdin/stdout. Every reply carries its command's `id` |
| `client/error-info.cjs` | How the runner reports a failed command, and whether the error is Stream's answer |
| `baseline/application-1729640-2026-09-25.json` | The application's configuration before the proof changed it (settings, grants, channel types). No users or data. Used by `restore` |
| `tests/` | Offline unit tests. They use no network and no `STREAM_*` variable; `tests/fakes.py` holds the fake server and client sessions |
| `checks/fix_reversals.py` | Shows that each P06.1-C1 and P06.1-C2 fix is tested (see "Checks (offline)") |
| `requirements*.in`, `requirements*.lock` | Python dependencies, hash-pinned |
| `package.json`, `package-lock.json`, `.npmrc` | JavaScript dependencies, exact versions |
| `.work/` | Ignored local output: snapshots, run results, the session usage ledger |

## SDKs

Both SDKs were chosen from Stream's current official documentation, read on 25 September 2026:

| Side | Package | Version | Documentation |
|---|---|---|---|
| Server | `getstream` (PyPI; GitHub `GetStream/stream-py`) | 6.1.0 | [Python getting started](https://getstream.io/chat/docs/python/): "The official Python SDK for Stream covers Chat, Video, Moderation, and Feeds" |
| Client | `stream-chat` (npm) | 9.53.0 | [Plain JS introduction](https://getstream.io/chat/docs/javascript/) |
| Client transport | `ws` 8.21.3 and `https-proxy-agent` 5.0.1 | exact | The same versions `stream-chat` and `axios` already resolve. Pinned directly because the runner uses them to route the SDK's WebSocket through the session proxy |

The evidence record lists every page the proof relies on.

## Variables

| Process | Reads | Never has |
|---|---|---|
| Server (`python -m glow_stream_proof`) | `STREAM_APP_ID`, `STREAM_API_KEY`, `STREAM_API_SECRET` from its own environment. It refuses to run if `DATABASE_URL`, `HD_API_KEY` or `GEO_API_KEY` is present (checked by name), or if `STREAM_APP_ID` is not `1729640` | — |
| Client (`node client/runner.cjs`) | `PROOF_API_KEY` (the client-safe API key), `PROOF_USER_TOKEN` (that session's own user token, if any), `PROOF_MAX_API_CALLS`, and the passthrough `PATH`, `HOME`, `LANG`, `HTTPS_PROXY`, `https_proxy`, `NODE_EXTRA_CA_CERTS` | `STREAM_API_SECRET`: the server builds the client environment from an allowlist and refuses one that contains the secret's name or value. The runner itself exits with code 3 if the name is present |

The harness never prints, logs or writes the secret or a full token:

- output passes through a redactor, and anything written is leak-checked first;
- evidence shows token claims only;
- no tool that stores credentials (for example a Stream CLI login) is configured.

## Install

From this directory, with the pinned toolchain (Python 3.12.14, Node 24.19.0, npm 11.9.0):

```bash
python3.12 -m venv .venv
.venv/bin/python -m pip install --require-hashes -r requirements-dev.lock
.venv/bin/python -m pip check
npm ci --ignore-scripts
```

In a Claude Code cloud session, npm needs the proxy and CA variables. Pass them by reference, never printed ([local setup](../../docs/operations/local-development.md#claude-code-cloud-sessions)):

```bash
HTTPS_PROXY="$HTTPS_PROXY" NODE_EXTRA_CA_CERTS="$NODE_EXTRA_CA_CERTS" npm ci --ignore-scripts
```

Regenerating the locks was done deliberately, with uv 0.8.17 and npm 11.9.0, as follows:

```bash
uv pip compile requirements.in --python-version 3.12 --generate-hashes --output-file requirements.lock --no-header
uv pip compile requirements-dev.in --python-version 3.12 --generate-hashes --output-file requirements-dev.lock --no-header
npm install --ignore-scripts --package-lock-only --no-audit --no-fund
```

## Checks (offline)

```bash
env -i PATH="$PATH" HOME="$HOME" LANG=C.UTF-8 .venv/bin/python -m unittest discover -s tests -t . -v
.venv/bin/ruff check .
.venv/bin/ruff format --check .
.venv/bin/mypy
node --check client/runner.cjs
node --check client/error-info.cjs
```

Install first: some tests start `client/runner.cjs` offline (with a placeholder API key and no connect) and read the installed `stream-chat` source, so they need `node_modules`.

The tests run in a clean environment. They assert that no `STREAM_*` variable is present, and they disable outbound sockets; the server client in `test_server_api` runs on an `httpx.MockTransport`. `test_run_simulation` drives the whole orchestration against fakes (`tests/fakes.py`); it does not test Stream.

`checks/fix_reversals.py` shows that each P06.1-C1 and P06.1-C2 fix is tested: in a scratch copy it reverts one fix at a time and runs that fix's tests, which must fail, then restores the fix and runs them again, which must pass. It changes nothing in this directory:

```bash
.venv/bin/python checks/fix_reversals.py
```

## Live commands

Every command reads `STREAM_*` from the server process's own environment. Commands that change the application are dry runs unless given `--apply`, except `run`.

```bash
.venv/bin/python -m glow_stream_proof baseline                 # read-only snapshot into .work/, without other users' identifiers or names
.venv/bin/python -m glow_stream_proof configure                # print the plan (dry run)
.venv/bin/python -m glow_stream_proof configure --apply        # apply, re-read and verify
.venv/bin/python -m glow_stream_proof run --accept-dashboard-user
.venv/bin/python -m glow_stream_proof verify-clean             # no proof users, channels, polls or user groups remain
.venv/bin/python -m glow_stream_proof cleanup [--apply]        # hard-delete leftover proof users and channels
.venv/bin/python -m glow_stream_proof restore [--apply] [--delete-match-type]   # --apply re-reads and verifies
```

`run`:

1. Preflight. The run refuses unless the configuration verifies, and unless the application holds no data the run did not create. With `--accept-dashboard-user`, the run stops unless exactly one user has role `admin` and `custom.dashboard_user` true, and that user was created in the minute recorded for the user Nathan confirmed on 25 September 2026 (24 September 2026, 13:07 UTC). No identifier is recorded. That user is never changed or deleted, and only its role, dashboard flag and creation time are compared. (Corrected in P06.1-C1: at I1's head the flag accepted any number of dashboard-flagged administrators.)
2. Setup. Creates synthetic users A, B, X and D (role `user`) with run-prefixed IDs, and issues each a 900-second token. Creates match channels AB and XD with exactly two members each.
3. The authorized path, then the bypass matrix, then the reconnect check, then the destructive cases.
4. Finish, whatever stopped the run (a stop condition, a guardrail, an error, a timeout or Ctrl-C):
   - every temporary change still in the journal is restored and verified (see below). A restore that fails is tried again after 10 s and 20 s when the failure was a rate limit (HTTP 429 or Stream code 9) or not a stop signal at all (for example a 5xx, or a re-read that still shows the change). After any other stop signal (a charge signal, or the API-call budget) it is not tried again (changed in P06.1-C2: until then every charge signal was retried). A restore that was made and accepted, but whose verification could not be made, leaves the journal and is reported **not verified**, not "not restored" (P06.1-C2);
   - cleanup, unless a charge or limit signal stopped the run at once. It hard-deletes the run's polls and user groups (including any a client managed to create), its channels and its users, including any user whose ID contains the run prefix (Stream prefixes guest IDs), and the `deleted-user-1729640-…` system user Stream creates during that delete. Each step is guarded, so a failure is recorded and the next step still runs. It then confirms that no proof user or channel remains, and no poll or user group that was not already there at preflight (preflight lists them; only counts are shown);
   - the configuration is re-read and compared with the target (`configuration.verify()`).

It prints the redacted results table and writes `.work/run-<prefix>.json` and `.md`, with progress after every case. The results also list every stop recorded, any temporary change not restored or not verified, and every problem found after the run. `run-<prefix>.json` is first written before the end of the run starts (marked `end_of_run: not finished`) and rewritten when it ends, so a second Ctrl-C inside the end of the run loses nothing observed (every `.work` file is written through a temporary file and then renamed, so an interrupted write leaves the previous file whole); that Ctrl-C stops the end of the run, closes the client processes, writes the results with the problem "the end of the run was interrupted" and exits 2 (P06.1-C2).

A case interrupted before it finished (a guardrail stop, a failed restore, an ended client session, any other exception or Ctrl-C) still records its row, with what it had observed: a FAIL stays a FAIL, and anything else becomes INCONCLUSIVE with the interruption as its reason (P06.1-C2; until then only a failed restore kept the row). See "Interrupted cases" under "Verdict rules".

Exit codes of `run`: `0` only if the run completed, every temporary change was restored and verified, cleanup was complete (every delete task `completed`, nothing left) and the configuration verifies; `2` if the run stopped (the output says why, and lists anything found after the run); `4` if it completed but a check after it failed or could not be made.

If the output reports a temporary change not restored, `configure` (a dry run) shows what differs from the target, and `configure --apply` returns guest creation and every `glow-match` feature to it. `restore --apply` does not: it returns the recorded pre-proof baseline. AB's overrides end with AB's deletion.

## Verdict rules

The matrix quality rule is unchanged: a refusal counts only when Stream returns its authentication or permission error, and every negative case pairs with a positive control. P06.1-C1 made these rules explicit and stricter, and P06.1-C2 stricter again; no HOLDS rule is weaker than at I1's head. Two FAIL rules now need their evidence (P06.1-C2): E5 with an unreadable stored user, and T4-rest-unread without both controls, are INCONCLUSIVE instead of FAIL, which is still not a pass.

- **Stream's answer, not the SDK's error** (new in P06.1-C1). The status and code are those of Stream's recorded response to the request under test: the one HTTP request the command sent. The SDK's own error is never used. A command that sent no request, or whose request has no recorded response (a local SDK throw, or a call that returned without sending), is **INCONCLUSIVE**, never HOLDS. Every command judged this way must send exactly one request; a reply with more than one recorded request has no answer either (P06.1-C2). A positive control counts only if Stream's recorded answer to it was 2xx.
- **WebSocket connects.** Success is the handshake Stream sent. A refusal counts only when the SDK built the error from Stream's own error frame; any other connect failure has no recorded answer.
- **Token refusals** are 401 with Stream code 5, 40, 41, 42 or 43. Code 2 is Stream's API-key error, so it is not attributable to the token (changed in P06.1-C1). Permission refusals are 403 with code 17 or 70.
- **HOLDS:** an attributable 401 or 403 and a successful control.
- **HOLDS (filtered, not refused):** 2xx without any of the case's leak terms, while the control found them. The guest and anonymous `read-ab` terms include AB's ID, A's and B's IDs and names, and both message IDs as well as their text; the `message` terms include XD's message ID, X's ID and XD's ID (widened in P06.1-C1).
- **HOLDS (accepted, not applied):** 2xx, but the claim or change had no effect. For E5 and S14 both the stored user and the connection's own user object in Stream's handshake must be unchanged (P06.1-C1); a change in either is a FAIL. If A's stored user cannot be read (Stream's listing does not include it), the case is INCONCLUSIVE, "A's stored user could not be read", unless the connection's user object already showed the change, which is a FAIL (P06.1-C2; until then an unreadable E5 user counted as a changed role, a FAIL, and an unreadable S14 user as unchanged).
- **REFUSED (feature off; not a permission error):** a 400 feature error (code 18 or 19).
- **INCONCLUSIVE:** no recorded answer, a refusal that is not attributable, a control that did not succeed, a client session ended by a timeout or a mismatched reply, or a case interrupted before it finished without an observed FAIL.
- **FAIL:** the action succeeded, or a response disclosed a leak term.

Cases with their own rule:

- **Interrupted cases** (P06.1-C2). Every way a case can end records its row: a guardrail stop, a failed restore, an ended client session, any other exception or Ctrl-C. The row keeps what the case had observed before the interruption (its request, Stream's answer and any evidence); a FAIL stays a FAIL, and anything else becomes INCONCLUSIVE, "interrupted before the case finished: …". The detail names the interruption. With nothing observed yet, the row is INCONCLUSIVE with the interruption as its reason. A guardrail stop, a failed restore and Ctrl-C then stop the run; after an ended client session or a harness error the run goes on. A progress file that cannot be written while a stop is in flight is noted and never replaces the stop.
- **A client success that must be undone** (P06.1-C2). When a client action that must be refused succeeds, the case's undo requests reverse it after the control, and the row records each undo's status. If the control is interrupted first, the undo follows the rule for what may still run after each kind of stop: after a guardrail stop it is not made (a charge or limit signal stops the run at once and deletes none of its data; the API-call budget has no calls left), and after Ctrl-C it is not made; after anything else (an ended client session, a failed restore, a harness error) it is made. The row says which, and why. The change is always to the run's own synthetic users, channels, messages, polls or groups, which cleanup deletes (after a charge or limit signal, `cleanup --apply`).
- **Feature-gated cases** (S2, S5, S6, S7, S12, and S10's poll vote). The feature-on phase is judged as above. The same request is then sent under the production configuration, where it must also fail: a success there is a FAIL, and a request with no recorded answer is INCONCLUSIVE, "no answer from Stream was recorded for the request under the production configuration", unless the feature-on phase already showed a FAIL (P06.1-C2).

- **G1:** judged on the client's own `POST /guest`, which must be the one HTTP request the command recorded (P06.1-C2). It FAILs whenever that request created a guest, whatever the connect `setGuestUser` makes afterwards did (P06.1-C1).
- **G2:** the guest from G1's control must be able to connect; under the lockdown its connect is refused, so G2 is "not run". I2a sets G2 up differently.
- **G3:** INCONCLUSIVE unless the anonymous connect succeeded, because the SDK otherwise rethrows the connect's error for every probe without sending anything (P06.1-C1).
- **RT1** (no refusal involved): HOLDS when A received AB's event and nothing about XD while X received XD's event; FAIL if any event A received carries XD's ID or text.
- **RT2 and RT3** ask what reaches B. FAIL if any event Stream delivered to B, of any type, in any window collected (after A's request and after the probe), carries the marker (P06.1-C1: every window and every event type is searched). Otherwise:
  - INCONCLUSIVE if A's request has no recorded answer, or B's listener did not see the probe message;
  - if Stream accepted the request: HOLDS if the named events arrived without the marker, and HOLDS (accepted, not applied) if none arrived;
  - if Stream refused it with an attributable error (`auth`, `permission` or `feature`: 401 with a token code, 403 with code 17 or 70, 400 with code 18 or 19): HOLDS, as nothing carrying the marker reached B while B was listening;
  - if Stream refused it any other way (`input`, `not-found` or `other`: a 400 input error, a 404, a 5xx): INCONCLUSIVE, "refusal not attributable". A malformed request or an outage says nothing about what a well-formed event delivers (changed in P06.1-C2: until then any refusal, and any named event after a refusal, was HOLDS).
- **Events** count only when Stream delivered them. The SDK's local events (`channels.queried`, `capabilities.changed`, `connection.changed`, `message.read_locally` and the rest of stream-chat 9.53.0's local list, plus health checks) are dropped, and the event type that carried a marker is recorded (P06.1-C1).
- **T4-ws:** Stream authenticating the connection as the token's user, not the claimed one, is HOLDS (accepted, not applied).
- **T4-rest-unread:** neither kind of HOLDS unless A's and B's own identical requests succeeded (the controls). A refusal of the claim HOLDS only with both controls (P06.1-C1). An accepted claim needs both controls and all three unread totals (A's, B's and the claim's, each from a 2xx answer) and A's and B's totals must differ: the claim's total equal to A's is HOLDS (accepted, not applied), equal to B's is a FAIL, anything else INCONCLUSIVE. Without both controls or all three totals the case is INCONCLUSIVE (P06.1-C2; until then a failed control or a missing total could give HOLDS (accepted, not applied) or a FAIL).
- **S15:** FAIL if B reads the marker by any of its reads; the result names each read, and for events the event type.

## Budget guardrails

Per session, the harness counts synthetic users, channels, concurrent connections and API calls, and stops before passing any of them:

| Resource | Limit per session |
|---|---|
| Synthetic users | 20 |
| Channels | 30 |
| Concurrent connections | 10 |
| API calls | 5,000 |

Server calls are counted before they are sent. Client calls are capped per command inside the runner. The count persists in the ignored `.work/usage-ledger.json`, so it covers every run of one checkout; a fresh clone starts at zero.

A response that suggests a charge, an upgrade or an exceeded limit stops the run at once: HTTP 402 or 429, Stream code 9 or 99, or wording about billing, quotas or upgrades. The check covers every server response, including the typed SDK calls such as `upsert_users` and `send_message` (P06.1-C1), and every client request. After such a stop the run deletes none of its users or channels, sends no undo of a client success, but it still restores any temporary change in its journal and re-reads the configuration. A restore left undone would leave the application less locked down than recorded.

The calls this costs (corrected in P06.1-C2: the README said "at most two or three calls per journalled change"). One restore attempt is at most three calls: the restoring `PUT` or `PATCH`, a re-read and, for AB's `read-channel-members` grant, B's members query. A journalled change gets one attempt when its case ends and, if that fails, one at the end of the run. The end of the run tries twice more, 10 s and 20 s apart, only when that attempt's own failure was a rate limit (HTTP 429 or Stream code 9) or not a stop signal (a 5xx, or a re-read that still shows the change). So a journalled change costs at most six calls when its restores are refused with a charge signal or stopped by the budget, and at most twelve otherwise. Then two reads of the configuration.

The matrix stops early enough to keep 130 API calls for the end of the run, plus 30 for the case in progress. The measured worst case for the end of the run, with every delete task polled 30 times and a journalled restore failing all three attempts, is 115 calls (`tests/test_cleanup.py`).

## What a run and `configure --apply` change, and how to restore

`configure --apply` sets:

- `disable_auth_checks=false` and `disable_permissions_checks=false`. Both were already false.
- `guest_user_creation_disabled=true`. It was false.
- Empty `.app` grants for `user`, `guest` and `anonymous`. `user` had 24 grants, including `search-user`, `update-user-owner` and `create-user-group`. `guest` had 4.
- Empty grants for every role in the five default channel types. Their features are unchanged.
- The `glow-match` channel type: members get `read-channel` only, every other role gets nothing, and every content feature is off, including typing events. Read events stay on.

The configuration stays in place for P06.1-I2.

During `run`, some cases change settings for a few seconds (corrected in P06.1-C1: at I1's head only the type features and guest creation were re-read after their restore, channel-override removals were never re-read, and a failed restore did not stop the run):

- the `config_overrides` of channel AB (replies, reactions, uploads, a `read-channel-members` grant);
- `glow-match` custom events and polls;
- guest creation, for the guest control.

Each change is written to the run's journal before its enabling request is sent. When its case ends, however it ends, the change is restored and verified:

- the type's features and the app's guest setting are re-read and must show the production values;
- AB is re-read while its override is set, and again after the removal. A re-read proves the removal of a key only if it showed that key as overridden while it was set; the key must then read clear. If the re-read did not show the `read-channel-members` grant, B's members query must be refused again. Any other key the re-read cannot show is recorded as **not verified** (the removal request was accepted), and the run exits non-zero at its end. The re-reads' shape (key names only, no values) is kept in the case's detail, because Stream's response shape for this read has not yet been seen live.

A restore that fails, or that reads back wrong, stops the run. If a guardrail stop was already in flight, both are recorded and the guardrail stays the run's stop. Anything still in the journal is restored at the end of the run, after a timeout or Ctrl-C too. A removal of AB's override that Stream accepted, but that could not be verified (for example, B's members query was stopped by a guardrail, while no key still reads as overridden), is not "not restored": it leaves the journal, is recorded as not verified, and the run exits non-zero (P06.1-C2).

The undo requests that reverse a control's change (message text, roles, memberships, channel data, uploads, A's member field) are checked too. A failed undo stops the run once its case is recorded. So does a failed restore of A's role in E5, when the role reached Stream's stored state (P06.1-C2: until then an exception there was recorded as a harness error and the run went on with A holding the role). The undo of a client success follows "A client success that must be undone" under "Verdict rules".

The run's own users, channels, polls and user groups are deleted.

To restore the recorded baseline, check the plan first, then apply it:

```bash
.venv/bin/python -m glow_stream_proof restore                            # plan only
.venv/bin/python -m glow_stream_proof restore --apply                    # grants and guest setting
.venv/bin/python -m glow_stream_proof restore --apply --delete-match-type
```

`--delete-match-type` works only when no `glow-match` channel exists. Stream's documented alternative is to send `grants: null` for a scope, which resets it to Stream's defaults. The live grants were not checked against Stream's defaults.

Side effect: the admin role's grants in the default types and in `glow-match` are empty too. A dashboard tool that acts client-side as the dashboard user may therefore be refused in those types until restored. This is unverified.

## What this proof does not show

- Revocation after unmatch, block, suspension or deletion; history policy; token revocation; a send racing a revocation; provider outage; economics. These belong to P06.1-I2.
- Video calls, feeds and other Stream products that the same user token can reach. They were not tested or configured.
- Real persistence, concurrency or restore (P11). Only this development application, its plan and synthetic users at the time of the run.
- Push notifications (P06.3) and webhooks. None were configured.
- That the app's own mobile client renders nothing it should not. The proof exercises the SDK and the API directly, as a modified client would.

## Limits (added in P06.1-C1)

- The client processes are isolated by their environment only: they run as the same operating-system user as the server process, with the secret kept out of their environment by an allowlist and the runner's refusal.
- `verify-clean` cannot see soft-deleted channels. C13's control soft-deletes AB before cleanup; cleanup hard-deletes every channel the run recorded, by ID, and requires the delete task to report `completed`.
- Charge detection reads HTTP statuses, Stream codes and error wording. It cannot see a charge Stream does not signal in a response.
- The client endpoints listed in the I1 review's finding 9 were never tried (I2a's work), and G2 and S10 need new setups (I2a).
- The poll and user-group listings (`POST /api/v2/polls/query`, `GET /api/v2/usergroups`, paths from `getstream` 6.1.0) and the channel re-read used to verify override removals (`POST /api/v2/chat/channels` filtered by `cid`) have not yet been run live. A listing Stream does not answer with 2xx is reported as not verified, and so is an override removal the re-read cannot show; either makes the run exit non-zero.
- The standalone `verify-clean` command has no preflight to compare with, so it reports every poll and user group present.
- Cleanup also hard-deletes the application-wide `deleted-user-1729640-…` user when it was created after the run started. That is safe here only because preflight guarantees the application holds no other data.

Added in P06.1-C2:

- Redaction by key name hides a value from every check that reads the redacted data, the leak checks included. The harness's own marker fields (`glow_note`, `glow_text`, `glow_bio`, `text`) do not match a credential pattern, and a test keeps it so; a new case must not put a marker under a key ending in `_key`, `_token` or holding `secret`, `password` or `credential`. Since P06.1-C2 any key ending in `_key` is redacted, so the client-safe API key in recorded request parameters (`api_key`) is redacted too.
- Credentials embedded in URL values (for example a webhook or queue URL) are not redacted by key name. No output path writes the raw application object; `baseline` writes only the settings the proof reads.
- After a guardrail stop or Ctrl-C during a case's control, a client success is not undone (see "Verdict rules"). The same holds for the restores inside S14 and E5 of A's own name and role: after an interruption they are left to cleanup, which deletes A.
