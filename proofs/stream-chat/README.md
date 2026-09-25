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
| `client/runner.cjs` | Client side (Node, Stream's client SDK `stream-chat`): one process per client session, driven over stdin/stdout |
| `baseline/application-1729640-2026-09-25.json` | The application's configuration before the proof changed it (settings, grants, channel types). No users or data. Used by `restore` |
| `tests/` | Offline unit tests. They use no network and no `STREAM_*` variable |
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
```

The tests run in a clean environment. They assert that no `STREAM_*` variable is present, and they disable outbound sockets. `test_run_simulation` drives the whole orchestration against fakes; it does not test Stream.

## Live commands

Every command reads `STREAM_*` from the server process's own environment. Commands that change the application are dry runs unless given `--apply`, except `run`.

```bash
.venv/bin/python -m glow_stream_proof baseline                 # read-only snapshot into .work/
.venv/bin/python -m glow_stream_proof configure                # print the plan (dry run)
.venv/bin/python -m glow_stream_proof configure --apply        # apply, re-read and verify
.venv/bin/python -m glow_stream_proof run --accept-dashboard-user
.venv/bin/python -m glow_stream_proof verify-clean             # no proof users or channels remain
.venv/bin/python -m glow_stream_proof cleanup [--apply]        # hard-delete leftover proof users and channels
.venv/bin/python -m glow_stream_proof restore [--apply] [--delete-match-type]
```

`run`:

1. Preflight. The run refuses unless the configuration verifies, and unless the application holds no data the run did not create. `--accept-dashboard-user` accepts the one Stream dashboard administrator user that Nathan confirmed on 25 September 2026. That user is never read in detail, changed or deleted.
2. Setup. Creates synthetic users A, B, X and D (role `user`) with run-prefixed IDs, and issues each a 900-second token. Creates match channels AB and XD with exactly two members each.
3. The authorized path, then the bypass matrix, then the reconnect check, then the destructive cases.
4. Cleanup. Hard-deletes the run's users and channels, including any user whose ID contains the run prefix (Stream prefixes guest IDs), and the `deleted-user-1729640-…` system user Stream creates during that delete. It then confirms that none remain.

It prints the redacted results table and writes `.work/run-<prefix>.json` and `.md`, with progress after every case.

## Budget guardrails

Per session, the harness counts synthetic users, channels, concurrent connections and API calls, and stops before passing any of them:

| Resource | Limit per session |
|---|---|
| Synthetic users | 20 |
| Channels | 30 |
| Concurrent connections | 10 |
| API calls | 5,000 |

Server calls are counted before they are sent. Client calls are capped per command inside the runner. The count persists in the ignored `.work/usage-ledger.json`, so it covers every run of one checkout; a fresh clone starts at zero.

A response that suggests a charge, an upgrade or an exceeded limit stops the run at once, without cleanup: HTTP 402 or 429, Stream code 9 or 99, or wording about billing, quotas or upgrades.

## What a run and `configure --apply` change, and how to restore

`configure --apply` sets:

- `disable_auth_checks=false` and `disable_permissions_checks=false`. Both were already false.
- `guest_user_creation_disabled=true`. It was false.
- Empty `.app` grants for `user`, `guest` and `anonymous`. `user` had 24 grants, including `search-user`, `update-user-owner` and `create-user-group`. `guest` had 4.
- Empty grants for every role in the five default channel types. Their features are unchanged.
- The `glow-match` channel type: members get `read-channel` only, every other role gets nothing, and every content feature is off, including typing events. Read events stay on.

The configuration stays in place for P06.1-I2.

During `run`, some cases change settings for a few seconds, then restore them and verify the restore:

- the `config_overrides` of channel AB (replies, reactions, uploads, a `read-channel-members` grant);
- `glow-match` custom events and polls;
- guest creation, for the guest control.

The run's own users and channels are deleted.

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
