# P06.1 evidence: chat-provider permissions proof

This is the evidence record for [P06.1](../../planning/p06-1-chat-provider-proof.md). It records observations only and is not an instruction source. Each implementation session adds its own section.

## P06.1-I1

The first implementation session. It enforced and recorded the application's checks, locked down every channel type, created the match type, proved the authorized path, ran the bypass matrix and cleaned up.

- **Session:** branch `claude/compassionate-lamport-531vtk`, started from `0f45e648099b415217938c25d7369164c0101def`.
- **Final live run:** the harness at commit `ed162e11c012a7858e3dbf1dd0ed7221eadb8a51`.
- **Later commits:** they changed only the harness fixes listed under "Deviations", the README and this record. No live run used them.
- **Application:** Nathan's development Stream application 1729640, synthetic users only.
- **Times:** 25 September 2026, all in UTC.

### Summary

- **Outcome 1, checks enforced: holds.** Authentication and permission checks were already on. Every bad token got `401`: a development token, a wrong-secret token and an expired token. Of the 85 cases in the final matrix, 65 held with an attributable `401` or `403` (code 5, 40, 43, 17 or 70) and a successful positive control. The other 20 are not refusals with a successful control: RT1, RT2 and RT3 held under their own rules (RT1 no refusal at all, RT2 `400` code 18, RT3 `201`); 4 were filtered `200`s and 3 were accepted but not applied; 9 were INCONCLUSIVE; and S15 got `200` (FAIL) (corrected in P06.1-C1). Code 17 is also not proof of the permission layer on its own: Stream documents `403` "Not Allowed" for disabled and frozen channels too, and code 17 was observed for "polls not enabled for this channel", "guest user creation is disabled for this application" and "this channel role can only be updated server side". Attribution rests on the controls (corrected in P06.1-C1).
- **Outcome 2, authorized path: holds.** All 18 checks PASS:
  - server-issued 900-second tokens;
  - server-created one-to-one channels;
  - app-mediated sends, with refusals that make no Stream call;
  - REST reads and WebSocket delivery;
  - disconnect and reconnect.
- **Outcome 3, no client bypass: does not hold. One design-level bypass remains.**
  - **S15:** a member can write up to 5 KB of free-text custom data on its own membership.
  - The other member receives it in the ordinary channel query response. Whether it also arrives in realtime events, such as `member.updated`, is unproven: the harness counted the SDK's own local `channels.queried` event, raised by B's query with the queried state, as delivered to B. I2a maps the event types (corrected in P06.1-C1).
  - No Stream permission governs that write. Removing `read-channel-members` blocks only the separate members endpoint.
  - Per the prompt, this line of work stopped here. It is reported as a design blocker under PF01.
  - The first live run found a second channel, typing events carrying free text. Turning typing events off closed it.
- **Other results in the final matrix:**
  - Guest creation is refused. Anonymous access reads nothing.
  - Nothing in any default type is reachable.
  - No self-escalation succeeded.
  - A learns nothing about X and D beyond the existence signals described below.
  - Nine cases are INCONCLUSIVE under the quality rule. They are explained case by case below.

### Environment check (names only)

| Check | Result |
|---|---|
| `DATABASE_URL`, `HD_API_KEY`, `GEO_API_KEY` | None present (the check printed nothing) |
| `STREAM_APP_ID`, `STREAM_API_KEY`, `STREAM_API_SECRET` | All three set |
| `command -v node npm npx python3.12` | `/root/.local/bin/node`, `/root/.local/bin/npm`, `/root/.local/bin/npx`, `/root/.local/bin/python3.12` (`$HOME` is `/root`) |
| Versions | node v24.19.0; npm 11.9.0; npx 11.9.0; Python 3.12.14 |
| Start gate | `git fetch origin claude/stoic-carson-66gdig`; `git merge --ff-only 0f45e648…` answered "Already up to date."; `git rev-parse HEAD` printed `0f45e648099b415217938c25d7369164c0101def` |
| Proxy variable names present | `HTTPS_PROXY`, `https_proxy`, `NO_PROXY`, `no_proxy`, `NODE_EXTRA_CA_CERTS`, `SSL_CERT_FILE`, `REQUESTS_CA_BUNDLE`, `CURL_CA_BUNDLE` (values not printed) |

The environment was never dumped. The only provider called was Stream, and only application 1729640. There were no database, HDE or Railway connections, no `playwright install`, `eas` or `migrate`, and no Stream CLI login.

### SDKs, versions and documentation

| Side | Package | Version | Chosen from |
|---|---|---|---|
| Server | `getstream` (PyPI, GitHub `GetStream/stream-py`) | 6.1.0 (released 9 September 2026) | [Python getting started](https://getstream.io/chat/docs/python/) names it "the official Python SDK for Stream" and shows `pip install getstream` |
| Client | `stream-chat` (npm) | 9.53.0 (npm `latest`, released 15 September 2026; newer releases were 10.0.0 release candidates) | [Plain JS introduction](https://getstream.io/chat/docs/javascript/) |
| Client transport | `ws` 8.21.3 and `https-proxy-agent` 5.0.1 | exact | The versions already in the dependency tree, pinned to route the SDK's WebSocket through the session proxy |

Locks and installs:

- `requirements.lock` and `requirements-dev.lock` were generated with `uv pip compile … --python-version 3.12 --generate-hashes --no-header`, using uv 0.8.17. The dev lock adds Ruff 0.16.8 and mypy 2.3.1.
- They were installed with `pip install --require-hashes` into the ignored `.venv`. `pip check` reported no broken requirements.
- `package-lock.json` was generated by npm 11.9.0 (`npm install --ignore-scripts --package-lock-only`) and installed with `npm ci --ignore-scripts`: 51 packages. `package.json` carries the engines Node 24.19.0 and npm 11.9.0.

Stream documentation relied on (the `.md` form of each page, read 25 September 2026):

- [Authentication and tokens](https://getstream.io/docs/platform/authentication/): server-side signing, `create_token(user_id, expiration=…)` adds `iat`, development tokens need auth checks disabled, and revocation needs `iat`.
- [Chat tokens and authentication (JavaScript)](https://getstream.io/chat/docs/javascript/tokens-and-authentication/): authentication error codes 5, 40, 41, 42, 43 and 2.
- [API error codes](https://getstream.io/docs/platform/api-error-codes/) and [error handling](https://getstream.io/docs/platform/error-handling/): 403 code 17 "Not Allowed", 403 code 70 "No access to channels", 400 code 4 input, 400 code 18 event not supported, 400 code 19 feature disabled.
- [Permissions and roles](https://getstream.io/docs/platform/permissions/) and [User permissions](https://getstream.io/chat/docs/python/chat-permission-policies/):
  - checks apply to client calls only;
  - a grants update changes only the roles it names;
  - `[]` removes a role's grants and `null` resets a scope;
  - channel-level grant modifiers; `config_overrides` is server-only.
- [Permissions reference](https://getstream.io/chat/docs/python/permissions-reference/): actions and default grants per scope. The live application's grants were read and used instead.
- [Channel types](https://getstream.io/chat/docs/python/channel-features/) and [Channel setting overwrites](https://getstream.io/chat/docs/python/channel-level-settings/): the features, which of them can be overridden per channel, and that a new type copies the `messaging` grants unless given its own.
- [App settings](https://getstream.io/chat/docs/python/app-setting-overview/): `disable_auth_checks` and `disable_permissions_checks`.
- [Users](https://getstream.io/docs/platform/users/) and [Authless users (JavaScript)](https://getstream.io/chat/docs/javascript/authless-users/):
  - guest and anonymous users;
  - guest creation can be disabled;
  - hard deletion gives orphaned channels a system-generated owner.
- [Initialization and users (JavaScript)](https://getstream.io/chat/docs/javascript/init-and-users/): `connectUser` "acts as an upsert for the user object".
- [Channel members (JavaScript)](https://getstream.io/chat/docs/javascript/channel-members/): member custom data (up to 5 KB), and `updateMemberPartial` can change "custom data and channel roles".
- The SDK sources as installed: `getstream` request, token and model code, and `stream-chat` 9.53.0 `dist/cjs/index.node.js`. They were read to confirm method names, request shapes and the SDK's local token check.

### Stop condition and Nathan's direction

The first read-only snapshot, at 02:51 UTC, showed one user the proof did not create. It is Stream's dashboard administrator user for the owner: role `admin`, custom flags `dashboard_user` and `staff_user`, first- and last-name fields, created 24 September 2026 at 13:07 UTC. There were no channels.

The prompt says to stop in that case. The session did so: it made no live change, built and tested the harness offline, and asked Nathan. His answer, about 03:12 UTC, was **"Proceed, leave it (Recommended)"**. The option he chose read: the proof never reads, changes or deletes that user; cleanup deletes only `p061i1-` users; the lockdown also empties the admin role's grants in the five default types and `glow-match`.

The harness accepts that dashboard user only with `--accept-dashboard-user`. At I1's head the flag accepted every user with role `admin` and `custom.dashboard_user` true, however many there were. Since P06.1-C1 the run stops unless exactly one such user exists and it was created in the minute recorded above (24 September 2026, 13:07 UTC) (corrected in P06.1-C1). Its identifier and name fields are not recorded here.

### Application settings before and after

Read through the server API: `GET /api/v2/app`, `/api/v2/chat/channeltypes`, `/api/v2/roles`, `/api/v2/users` and `POST /api/v2/chat/channels`.

| Setting | Before (02:51) | After (03:32, final) |
|---|---|---|
| `disable_auth_checks` | `false` (checks on) | `false` |
| `disable_permissions_checks` | `false` (checks on) | `false` |
| `permission_version` | `v2` | `v2` |
| `guest_user_creation_disabled` | `false` | `true` |
| `multi_tenant_enabled` | `false` | `false` |
| `user_search_disallowed_roles` | `[]` | `[]` |
| `revoke_tokens_issued_before` | `null` | `null` |
| `.app` grants, `user` | 24 grants, including `search-user`, `update-user-owner`, `create-user-group`, `read-user-groups`, `create-poll-any-team` and `upload-attachment-global-owner` | none |
| `.app` grants, `guest` | `flag-user`, `mute-user`, `search-user`, `update-user-owner` | none |
| `.app` grants, `anonymous` | none | none |
| `before_message_send_hook_url`, `webhook_url`, `event_hooks`, `custom_action_handler_url` | not present or empty | unchanged |
| Channel types | commerce, gaming, livestream, messaging, team | the same five, plus `glow-match` |
| Data | 1 dashboard user, 0 channels | 1 dashboard user, 0 channels |

Authentication and permission checks were already enforced, so neither needed changing. Both were re-read after every configuration step.

The complete before-state of settings, grants and channel types is committed as `proofs/stream-chat/baseline/application-1729640-2026-09-25.json`, without users or data. Grant counts per default type before the change:

| Type | Roles with grants (count) |
|---|---|
| commerce | admin 42, channel_member 19, channel_moderator 37, global_admin 42, global_moderator 39, global_read_only 4, guest 15, moderator 39, user 25 |
| gaming | admin 42, channel_member 20, channel_moderator 34, global_admin 42, global_moderator 35, global_read_only 4, moderator 35, user 23 |
| livestream | admin 42, anonymous 3, channel_member 1, channel_moderator 19, global_admin 41, global_moderator 34, global_read_only 4, guest 5, moderator 35, user 24 |
| messaging | admin 42, channel_member 21, channel_moderator 37, global_admin 42, global_moderator 42, global_read_only 4, moderator 42, user 30 |
| team | admin 42, channel_member 21, channel_moderator 37, global_admin 42, global_moderator 42, global_read_only 4, moderator 42, user 30 |

### Configuration applied

`python -m glow_stream_proof configure --apply` sends each request, then re-reads and verifies the result. It ran three times, and each time reported "differences after: []":

| Time | Version | Change |
|---|---|---|
| 03:13:23 | v1 | `PATCH /api/v2/app`: guest creation disabled; `.app` grants of `user`, `guest` and `anonymous` emptied; both checks asserted false. `PUT` on each default type: every role's grants emptied (admin, anonymous, channel_member, channel_moderator, global_admin, global_moderator, global_read_only, guest, moderator, user); features and commands unchanged. `POST` then `PUT` for `glow-match`. Typing on; members had `read-channel` and `read-channel-members` |
| 03:17:53 | v2 | `glow-match` `typing_events` set false, after the smoke run's finding (below) |
| 03:28:36 | v3 | `glow-match` `channel_member` grants reduced to `read-channel`, after run 2's S15 finding |

Final `glow-match` configuration (v3), as re-read at 03:32:

| Field | Value |
|---|---|
| Grants | `channel_member`: `read-channel`. Every other role (admin, anonymous, channel_moderator, global_admin, global_moderator, global_read_only, guest, moderator, user): none |
| Off | typing_events, connect_events, custom_events, reactions, replies, quotes, mutes, uploads, url_enrichment, polls, shared_locations, user_message_reminders, delivery_events (read receipts), count_messages, mark_messages_pending, push_notifications, reminders; commands `[]` |
| On | read_events, search |
| Other | automod disabled; max_message_length 5000; message_retention infinite |

Temporary changes made during runs, each reversed in the same run. Only the type-level toggles and the guest setting were verified by a re-read. The removal of AB's `config_overrides` was sent but neither its status checked nor AB re-read, and a failed restore would not have stopped the run; the review's finding 2 applies (corrected in P06.1-C1):

- Channel AB's `config_overrides`: replies, reactions or uploads enabled for one case each, then `{}` (runs 2 and final). A `read-channel-members` grant on AB for S15's control (final run).
- `glow-match` `custom_events` (S12) and `polls` (S10) set true for a few seconds. Each restore was verified by re-reading the type (runs 2 and final for custom events; final run for polls).
- `guest_user_creation_disabled` set false for G1's control for a few seconds around 03:29:12, then true again and verified (final run).

Kept for P06.1-I2: the v3 configuration above. How to restore:

- `python -m glow_stream_proof restore` prints the plan. `--apply` restores the recorded grants and the guest setting. `--delete-match-type` also deletes `glow-match`, which works only when no channel of that type exists.
- Stream's documented `grants: null` resets a scope to Stream's defaults instead. The recorded grants were not checked against those defaults.
- The restore plan is unit-tested offline but was **not executed**.

Side effect Nathan accepted: the admin role's grants are empty in the default types and in `glow-match`. A dashboard feature that acts client-side as the dashboard user may be refused there. This was not tested.

### Live runs

| Run | Time | Scope | Users / channels / API calls counted | Outcome |
|---|---|---|---|---|
| `p061i1-0925031346` (smoke) | 03:13:46–03:14:29 | 22 cases | 4 / 4 / 78 | All authorized-path checks PASS. Found typing free text (then fixed by v2). T4-ws was marked FAIL only because the harness did not yet record the connected identity. The upload control failed with 400 code 4, so the permission-layer phase was added. Cleanup confirmed. Stream's `deleted-user-1729640-…` system user, created by the hard delete, was then removed by hand |
| `p061i1-0925031802` | 03:18:02–about 03:20 | all cases | 6 / 8 / not separated (users counted conservatively, including two guest reservations) | The matrix ran to the end, but the reconnect check ran after the case that deletes AB and raised an exception before results were written. **The results of this run are lost.** Cleanup ran and confirmed, including the system user. The harness was fixed |
| `p061i1-0925032139` | 03:21:39–03:22:34 | 84 cases | 4 / 8 / 221 | Found S15 (member custom data). A's client process exited on an SDK unhandled rejection after the reconnect, so S4a, S4b, C12 and C13 recorded harness errors. Cleanup confirmed |
| `p061i1-0925032853` (final) | 03:28:53–03:30:32 | 85 cases | 4 (5 actual, see below) / 8 / 256 | Tables below. Cleanup left one guest user behind (see "Cleanup"). It was deleted by hand at about 03:31, and the result verified |

### Final run: authorized path

| Check | Description | Result | Evidence |
|---|---|---|---|
| AP1 | server creates four synthetic users with the ordinary user role | PASS | 4 users, roles ['user'] |
| AP2 | server issues each user a token with user_id, iat and exp (lifetime 900 s) | PASS | lifetimes (exp - iat) {'A': 905, 'B': 905, 'X': 905, 'D': 905} |
| AP3-AB | server creates AB (glow-match) with exactly its two members | PASS | members ['{A}', '{B}'] |
| AP3-XD | server creates XD (glow-match) with exactly its two members | PASS | members ['{D}', '{X}'] |
| AP4-A | client A connects over Stream's WebSocket and watches its own channel | PASS | connect ok (succeeded); watch 201 (succeeded); role user |
| AP4-B | client B connects over Stream's WebSocket and watches its own channel | PASS | connect ok (succeeded); watch 201 (succeeded); role user |
| AP4-X | client X connects over Stream's WebSocket and watches its own channel | PASS | connect ok (succeeded); watch 201 (succeeded); role user |
| AP5-A | app send path: A's message to AB passes the match/block check and is sent server-side | PASS | decision authorized; Stream called True |
| AP5-B | app send path: B's message to AB passes the match/block check and is sent server-side | PASS | decision authorized; Stream called True |
| AP5-X | app send path: X's message to XD passes the match/block check and is sent server-side | PASS | decision authorized; Stream called True |
| AP6 | app send path refuses A to XD (not a participant) without calling Stream | PASS | decision not_a_participant; Stream called False; API calls before 17, after 17 |
| AP7 | app send path refuses A to an unmatched pair's channel id without calling Stream | PASS | decision no_current_match; Stream called False; API calls before 17, after 17 |
| AP8 | app send path refuses a send after a block (fixture state) without calling Stream | PASS | decision blocked; API calls before 17, after 17 |
| AP9-A | client A reads AB over REST and sees B's server-sent message | PASS | query 201 (succeeded); B's text present True |
| AP9-B | client B reads AB over REST and sees A's server-sent message | PASS | query 201 (succeeded); A's text present True |
| AP10-A | client A receives the other member's server-sent message over the WebSocket | PASS | 6 events; message.new for the other's message 1 |
| AP10-B | client B receives the other member's server-sent message over the WebSocket | PASS | 6 events; message.new for the other's message 1 |
| AP11 | client A disconnects, reconnects over the WebSocket and receives the next message | PASS | disconnect ok (succeeded); reconnect ok (succeeded); watch 201 (succeeded); message.new received True |

`{A}`, `{B}` and the other braces stand for the run's synthetic identifiers. For example, `{A}` is `p061i1-0925032853-ua` and `{AB}` is `p061i1-0925032853-ch-ab`.

Token claims, as issued by `getstream`'s `create_token(user_id, expiration=900)`, shown without the tokens:

| User | alg | Claims | Signature |
|---|---|---|---|
| A | HS256 | `user_id` `p061i1-0925032853-ua`, `iat` 1790306928 (03:28:48 UTC), `exp` 1790307833 | present |
| B, X, D | HS256 | the same shape, with their own `user_id` | present |

`exp − iat` is 905 seconds, because the SDK back-dates `iat` by 5 seconds.

The bad tokens in the matrix were:

- **T1:** a development token that `StreamChat.devToken` made in the client, with the literal signature `devtoken`.
- **T2:** A's claims (`user_id`, `iat`, `exp`) signed with a random wrong secret.
- **T3:** A's claims signed correctly, with an `exp` 600 seconds in the past.

### Final run: bypass matrix

Every case was run from a client process holding only the API key and one user token (or none). Controls come in three kinds:

- **Server replay:** the same method, path and body re-sent with server authentication. A `user_id` is added where server-side calls require one.
- **Session:** the same SDK call by the authorized member.
- **Custom:** described in the row.

"Observed" is the HTTP status and Stream code of the client request. The verdicts, as recorded by the harness, mean:

- **HOLDS:** an attributable 401 or 403 and a successful control.
- **HOLDS (filtered, not refused):** 2xx without any of the target data, while the control found it.
- **HOLDS (accepted, not applied):** 2xx, but the claim or change had no effect.
- **INCONCLUSIVE:** the refusal is not attributable, or the control did not succeed.
- **FAIL:** the action succeeded.

Added in P06.1-C1: the legend above does not cover the realtime rows, which have their own rules (corrected in P06.1-C1).

- **RT1** involves no refusal. HOLDS meant A received AB's event and nothing about XD while X received XD's event.
- **RT2 and RT3** ask what reaches B. HOLDS meant that nothing carrying the free-text field arrived while B was shown to be listening: RT2's request was refused `400` code 18, and nothing arrived; RT3's was accepted `201`, and B's `message.read` arrived without the field.

For feature-gated cases, "feature on" is the permission-layer phase: the feature was enabled on AB, or on the type for a few seconds. "Feature off" is the production configuration.

#### Tokens

| Case | Actor | Token | Action | Expected | Request | Observed | Control | Verdict |
|---|---|---|---|---|---|---|---|---|
| T1-rest | A | development token for A | query own channel AB over REST with a development token (signature 'devtoken') | refused | POST /channels/glow-match/{AB}/query | 401 / code 5 | A valid token: 201 (succeeded) | HOLDS: auth error; control succeeded |
| T1-ws | A | development token for A | open a WebSocket connection as A with a development token (signature 'devtoken') | refused | WebSocket /connect | 401 / code 5 | A's valid token: ok (succeeded) | HOLDS: auth error; control succeeded |
| T2-rest | A | A's claims signed with a wrong secret | query own channel AB over REST with a token signed with a wrong secret | refused | POST /channels/glow-match/{AB}/query | 401 / code 5 | A valid token: 201 (succeeded) | HOLDS: auth error; control succeeded |
| T2-ws | A | A's claims signed with a wrong secret | open a WebSocket connection as A with a token signed with a wrong secret | refused | WebSocket /connect | 401 / code 43 | A's valid token: ok (succeeded) | HOLDS: auth error; control succeeded |
| T3-rest | A | A's token, expired | query own channel AB over REST with an expired but correctly signed token | refused | POST /channels/glow-match/{AB}/query | 401 / code 40 | A valid token: 201 (succeeded) | HOLDS: auth error; control succeeded |
| T3-ws | A | A's token, expired | open a WebSocket connection as A with an expired but correctly signed token | refused | WebSocket /connect | 401 / code 40 | A's valid token: ok (succeeded) | HOLDS: auth error; control succeeded |
| T4-ws | A | A's valid token | open a WebSocket connection claiming user B (local SDK check skipped) | identity-kept | WebSocket /connect | ok (succeeded) | B's own token as B: ok (succeeded) | HOLDS (accepted, not applied): claim ignored: Stream authenticated the connection as A (the token's user) |
| T4-rest-xd | A | A's valid token | query XD with user_id=X in the request (claims to act as X) | refused | POST /channels/glow-match/{XD}/query ?user_id={X} | 403 / code 17 | X: 201 (succeeded) | HOLDS: permission error; control succeeded |
| T4-rest-unread | A | A's valid token | read unread counts with user_id=B in the request (claims to act as B) | identity-kept | GET /unread ?user_id={B} | 200 (succeeded) | A's own total 0; B's own total 1 | HOLDS (accepted, not applied): claim ignored: the response is A's own unread count |

#### Guest and anonymous access (API key only, or a guest role)

| Case | Actor | Token | Action | Expected | Request | Observed | Control | Verdict |
|---|---|---|---|---|---|---|---|---|
| G1-create | none | API key only | create a guest user client-side (setGuestUser) | refused | POST /guest | 403 / code 17 | identical request with guest creation enabled (200): 403 / code 17; disabled again (200) and verified | INCONCLUSIVE: permission error, but the positive control did not succeed |
| G2-read-ab | guest | server-issued guest token | query channel AB | no-leak | - | not run: no guest session | - | INCONCLUSIVE: the guest control did not create a guest |
| G3-read-ab | anonymous | none (anonymous) | query channel AB | no-leak | POST /channels/glow-match/{AB}/query | 403 / code 17 | A: 201 (succeeded); control found target data True | HOLDS: permission error; control succeeded |
| G2-channels | guest | server-issued guest token | query channels with a type filter (corrected in P06.1-C1: the harness's text said "an empty filter") | no-leak | - | not run: no guest session | - | INCONCLUSIVE: the guest control did not create a guest |
| G3-channels | anonymous | none (anonymous) | query channels with a type filter (corrected in P06.1-C1: the harness's text said "an empty filter") | no-leak | POST /channels | 403 / code 70 | A: 403 / code 70; control found target data False | INCONCLUSIVE: permission error, but the positive control did not succeed |
| G2-users | guest | server-issued guest token | query users | no-leak | - | not run: no guest session | - | INCONCLUSIVE: the guest control did not create a guest |
| G3-users | anonymous | none (anonymous) | query users | no-leak | GET /users | 200 (succeeded) | server GET /users -> 200; control found target data True | HOLDS (filtered, not refused): succeeded with none of the target data; control found it |
| G2-message | guest | server-issued guest token | fetch XD's message by ID | no-leak | - | not run: no guest session | - | INCONCLUSIVE: the guest control did not create a guest |
| G3-message | anonymous | none (anonymous) | fetch XD's message by ID | no-leak | GET /messages/{m_x} | 403 / code 17 | X: 200 (succeeded); control found target data True | HOLDS: permission error; control succeeded |

#### Reading outside the match

| Case | Actor | Token | Action | Expected | Request | Observed | Control | Verdict |
|---|---|---|---|---|---|---|---|---|
| R1 | A | A's valid token | watch XD | refused | POST /channels/glow-match/{XD}/query | 403 / code 17 | X: 201 (succeeded) | HOLDS: permission error; control succeeded |
| R2 | A | A's valid token | query XD without watching | refused | POST /channels/glow-match/{XD}/query | 403 / code 17 | X: 201 (succeeded) | HOLDS: permission error; control succeeded |
| R3 | A | A's valid token | query channels whose members include X | no-leak | POST /channels | 403 / code 70 | X: 201 (succeeded); control found target data True | HOLDS: permission error; control succeeded |
| R4 | A | A's valid token | query channels whose members include D | no-leak | POST /channels | 403 / code 70 | X: 201 (succeeded); control found target data True | HOLDS: permission error; control succeeded |
| R5 | A | A's valid token | query channels by XD's cid | no-leak | POST /channels | 403 / code 70 | X: 201 (succeeded); control found target data True | HOLDS: permission error; control succeeded |
| R6 | A | A's valid token | fetch XD's message by its ID | refused | GET /messages/{m_x} | 403 / code 17 | X: 200 (succeeded) | HOLDS: permission error; control succeeded |
| R7a | A | A's valid token | search messages in XD's cid for XD's text | no-leak | GET /search | 400 / code 4 | X: 200 (succeeded); control found target data True | INCONCLUSIVE: refusal not attributable (input) |
| R7b | A | A's valid token | search every glow-match channel for XD's text | no-leak | GET /search | 200 (succeeded) | X: 200 (succeeded); control found target data True | HOLDS (filtered, not refused): succeeded with none of the target data; control found it |
| R8a | A | A's valid token | query users X and D | no-leak | GET /users | 200 (succeeded) | server replay GET -> 200; control found target data True | HOLDS (filtered, not refused): succeeded with none of the target data; control found it |
| R8b | A | A's valid token | query users by role (everyone with role user) | no-leak | GET /users | 200 (succeeded) | server replay GET -> 200; control found target data True | HOLDS (filtered, not refused): succeeded with none of the target data; control found it |
| R9 | A | A's valid token | query XD's members | refused | GET /members | 403 / code 17 | X: 403 / code 17 | INCONCLUSIVE: permission error, but the positive control did not succeed |

#### Realtime (WebSocket)

| Case | Actor | Token | Action | Expected | Request | Observed | Control | Verdict |
|---|---|---|---|---|---|---|---|---|
| RT1 | A | A's valid token | while connected, receive events for AB and none for XD | no-leak | WebSocket events | A: 1 events, AB message.new True | X received XD message.new True | HOLDS: A received AB's event and nothing for XD |
| RT2 | A | A's valid token | typing event carrying a free-text field (what B receives) | carries-no-free-text | POST /channels/glow-match/{AB}/event | 400 / code 18 | B listening (received a probe message): True | HOLDS: refused (feature); nothing delivered to B, who was listening |
| RT3 | A | A's valid token | read event carrying a free-text field (what B receives) | carries-no-free-text | POST /channels/glow-match/{AB}/read | 201 (succeeded) | B listening (received a probe message): True | HOLDS: delivered without the free-text field |

#### Putting content in front of B outside the app's path

| Case | Actor | Token | Action | Expected | Request | Observed | Control | Verdict |
|---|---|---|---|---|---|---|---|---|
| S1 | A | A's valid token | send a message to AB | refused | POST /channels/glow-match/{AB}/message | 403 / code 17 | server replay POST -> 201 | HOLDS: permission error; control succeeded |
| S2 | A | A's valid token | reply in a thread to B's server-sent message | refused | POST /channels/glow-match/{AB}/message | feature on: 403 / code 17; feature off (production): 400 / code 19 | server replay POST -> 201 | HOLDS: permission error; control succeeded |
| S3a | A | A's valid token | edit A's own server-sent message | refused | POST /messages/{m_a} | 403 / code 17 | server replay POST -> 201 (undo POST 201) | HOLDS: permission error; control succeeded |
| S3b | A | A's valid token | edit B's server-sent message | refused | POST /messages/{m_b} | 403 / code 17 | server replay POST -> 201 (undo POST 201) | HOLDS: permission error; control succeeded |
| S5 | A | A's valid token | react to B's message | refused | POST /messages/{m_b}/reaction | feature on: 403 / code 17; feature off (production): 400 / code 19 | server replay POST -> 201 (undo DELETE 200) | HOLDS: permission error; control succeeded |
| S6 | A | A's valid token | upload a file to AB | refused | POST /channels/glow-match/{AB}/file | feature on: 403 / code 17; feature off (production): 400 / code 4 | server upload -> 201 (undo DELETE 200) | HOLDS: permission error; control succeeded |
| S7 | A | A's valid token | upload an image to AB | refused | POST /channels/glow-match/{AB}/image | feature on: 403 / code 17; feature off (production): 400 / code 4 | server upload -> 201 (undo DELETE 200) | HOLDS: permission error; control succeeded |
| S8 | A | A's valid token | pin B's message | refused | PUT /messages/{m_b} | 403 / code 17 | server replay PUT -> 201 (undo PUT 201) | HOLDS: permission error; control succeeded |
| S9 | A | A's valid token | create a poll | refused | POST /polls | 403 / code 17 | server replay POST -> 201 | HOLDS: permission error; control succeeded |
| S10 | A | A's valid token | vote on a poll in AB | refused | - | not set up | polls on (201); poll 201; poll message 403 / code 17 (SendMessage failed with error: "polls not enabled for this channel"); restored {'polls': False} (201, verified) | INCONCLUSIVE: no poll message could be created in AB |
| S11 | A | A's valid token | send a slash command (/giphy) to AB | refused | POST /channels/glow-match/{AB}/message | 403 / code 17 | server replay POST -> 201 | HOLDS: permission error; control succeeded |
| S12 | A | A's valid token | send a custom event with free text to AB | refused | POST /channels/glow-match/{AB}/event | feature on: 403 / code 17; feature off (production): 400 / code 18 | server replay POST -> 201 | HOLDS: permission error; control succeeded |
| S13 | A | A's valid token | change A's own name and a custom profile field | refused | PATCH /users | 403 / code 17 | server replay PATCH -> 200 (undo PATCH 200) | HOLDS: permission error; control succeeded |
| S14 | A | A's valid token | change A's own profile by connecting with new name, image and custom field | not-effective | WebSocket /connect (user object with name, image, custom field) | 403 / code 17 | server PATCH /users -> 200; name applied True | HOLDS: permission error; stored state unchanged |
| S15 | A | A's valid token | set a free-text custom field on A's own membership in AB (can B read it?) | no-leak | PATCH /channels/glow-match/{AB}/member | 200 (succeeded) | with read-channel-members granted on AB (200): A's write 200 (succeeded); B found it via ['channel_query', 'query_members', 'events']; override removed (200) | FAIL: response disclosed: B read it via channel_query, B read it via events |
| S16 | A | A's valid token | create a user group containing A and B | refused | POST /usergroups | 403 / code 17 | server replay POST -> 201 | HOLDS: permission error; control succeeded |
| S4a | A | A's valid token | delete A's own server-sent message | refused | DELETE /messages/{m_a} | 403 / code 17 | server replay DELETE -> 200 | HOLDS: permission error; control succeeded |
| S4b | A | A's valid token | delete B's server-sent message | refused | DELETE /messages/{m_b} | 403 / code 17 | server replay DELETE -> 200 | HOLDS: permission error; control succeeded |

#### Self-escalation

| Case | Actor | Token | Action | Expected | Request | Observed | Control | Verdict |
|---|---|---|---|---|---|---|---|---|
| E1 | A | A's valid token | set A's own role to admin (partial update) | refused | PATCH /users | 403 / code 17 | server replay PATCH -> 200 (undo PATCH 200) | HOLDS: permission error; control succeeded |
| E2 | A | A's valid token | set A's own role to admin (upsert) | refused | POST /users | 403 / code 17 | server replay POST -> 201 (undo PATCH 200) | HOLDS: permission error; control succeeded |
| E3 | A | A's valid token | set A's own teams | refused | PATCH /users | 403 / code 17 | server replay PATCH -> 200 (undo PATCH 200) | HOLDS: permission error; control succeeded |
| E6 | A | A's valid token | set A's own channel_role to channel_moderator (member partial update) | refused | PATCH /channels/glow-match/{AB}/member | 403 / code 17 | server replay PATCH -> 200 (undo PATCH 200) | HOLDS: permission error; control succeeded |
| E4 | A | A's valid token | assign A the channel_moderator role in AB | refused | POST /channels/glow-match/{AB} | 403 / code 17 | server replay POST -> 201 (undo POST 201) | HOLDS: permission error; control succeeded |
| E5 | A | A's valid token | connect claiming role admin in the user object | not-effective | WebSocket /connect (user object with role admin) | ok (succeeded) | E1 server replay succeeded: True | HOLDS (accepted, not applied): request accepted but the stored state is unchanged |

#### Creating, joining and changing channels (match type and every default type)

| Case | Actor | Token | Action | Expected | Request | Observed | Control | Verdict |
|---|---|---|---|---|---|---|---|---|
| C1 | A | A's valid token | create a glow-match channel with members A and B | refused | POST /channels/glow-match/{prefix}-c1/query | 403 / code 17 | server replay POST -> 201 | HOLDS: permission error; control succeeded |
| C2-create | A | A's valid token | create a commerce channel with members A and B | refused | POST /channels/commerce/{prefix}-c2/query | 403 / code 17 | server replay POST -> 201 | HOLDS: permission error; control succeeded |
| C2-read | A | A's valid token | read that commerce channel as one of its members | refused | POST /channels/commerce/{prefix}-c2/query | 403 / code 17 | server replay POST -> 201 | HOLDS: permission error; control succeeded |
| C2-send | A | A's valid token | send in that commerce channel as one of its members | refused | POST /channels/commerce/{prefix}-c2/message | 403 / code 17 | server replay POST -> 201 | HOLDS: permission error; control succeeded |
| C2-join | X | X's valid token | join that commerce channel (add own membership) | refused | POST /channels/commerce/{prefix}-c2 | 403 / code 17 | server replay POST -> 201 (undo POST 201) | HOLDS: permission error; control succeeded |
| C3-create | A | A's valid token | create a gaming channel with members A and B | refused | POST /channels/gaming/{prefix}-c3/query | 403 / code 17 | server replay POST -> 201 | HOLDS: permission error; control succeeded |
| C3-read | A | A's valid token | read that gaming channel as one of its members | refused | POST /channels/gaming/{prefix}-c3/query | 403 / code 17 | server replay POST -> 201 | HOLDS: permission error; control succeeded |
| C3-send | A | A's valid token | send in that gaming channel as one of its members | refused | POST /channels/gaming/{prefix}-c3/message | 403 / code 17 | server replay POST -> 201 | HOLDS: permission error; control succeeded |
| C3-join | X | X's valid token | join that gaming channel (add own membership) | refused | POST /channels/gaming/{prefix}-c3 | 403 / code 17 | server replay POST -> 201 (undo POST 201) | HOLDS: permission error; control succeeded |
| C4-create | A | A's valid token | create a livestream channel with members A and B | refused | POST /channels/livestream/{prefix}-c4/query | 403 / code 17 | server replay POST -> 201 | HOLDS: permission error; control succeeded |
| C4-read | A | A's valid token | read that livestream channel as one of its members | refused | POST /channels/livestream/{prefix}-c4/query | 403 / code 17 | server replay POST -> 201 | HOLDS: permission error; control succeeded |
| C4-send | A | A's valid token | send in that livestream channel as one of its members | refused | POST /channels/livestream/{prefix}-c4/message | 403 / code 17 | server replay POST -> 201 | HOLDS: permission error; control succeeded |
| C4-join | X | X's valid token | join that livestream channel (add own membership) | refused | POST /channels/livestream/{prefix}-c4 | 403 / code 17 | server replay POST -> 201 (undo POST 201) | HOLDS: permission error; control succeeded |
| C5-create | A | A's valid token | create a messaging channel with members A and B | refused | POST /channels/messaging/{prefix}-c5/query | 403 / code 17 | server replay POST -> 201 | HOLDS: permission error; control succeeded |
| C5-read | A | A's valid token | read that messaging channel as one of its members | refused | POST /channels/messaging/{prefix}-c5/query | 403 / code 17 | server replay POST -> 201 | HOLDS: permission error; control succeeded |
| C5-send | A | A's valid token | send in that messaging channel as one of its members | refused | POST /channels/messaging/{prefix}-c5/message | 403 / code 17 | server replay POST -> 201 | HOLDS: permission error; control succeeded |
| C5-join | X | X's valid token | join that messaging channel (add own membership) | refused | POST /channels/messaging/{prefix}-c5 | 403 / code 17 | server replay POST -> 201 (undo POST 201) | HOLDS: permission error; control succeeded |
| C6-create | A | A's valid token | create a team channel with members A and B | refused | POST /channels/team/{prefix}-c6/query | 403 / code 17 | server replay POST -> 201 | HOLDS: permission error; control succeeded |
| C6-read | A | A's valid token | read that team channel as one of its members | refused | POST /channels/team/{prefix}-c6/query | 403 / code 17 | server replay POST -> 201 | HOLDS: permission error; control succeeded |
| C6-send | A | A's valid token | send in that team channel as one of its members | refused | POST /channels/team/{prefix}-c6/message | 403 / code 17 | server replay POST -> 201 | HOLDS: permission error; control succeeded |
| C6-join | X | X's valid token | join that team channel (add own membership) | refused | POST /channels/team/{prefix}-c6 | 403 / code 17 | server replay POST -> 201 (undo POST 201) | HOLDS: permission error; control succeeded |
| C7 | A | A's valid token | add X to AB | refused | POST /channels/glow-match/{AB} | 403 / code 17 | server replay POST -> 201 (undo POST 201) | HOLDS: permission error; control succeeded |
| C8 | A | A's valid token | add itself to XD | refused | POST /channels/glow-match/{XD} | 403 / code 17 | server replay POST -> 201 (undo POST 201) | HOLDS: permission error; control succeeded |
| C9 | A | A's valid token | remove B from AB | refused | POST /channels/glow-match/{AB} | 403 / code 17 | server replay POST -> 201 (undo POST 201) | HOLDS: permission error; control succeeded |
| C10a | A | A's valid token | change AB's data (partial update: name and a custom field) | refused | PATCH /channels/glow-match/{AB} | 403 / code 17 | server replay PATCH -> 200 (undo PATCH 200) | HOLDS: permission error; control succeeded |
| C10b | A | A's valid token | change AB's data (full update) | refused | POST /channels/glow-match/{AB} | 403 / code 17 | server replay POST -> 201 (undo PATCH 200) | HOLDS: permission error; control succeeded |
| C11 | A | A's valid token | freeze AB | refused | PATCH /channels/glow-match/{AB} | 403 / code 17 | server replay PATCH -> 200 (undo PATCH 200) | HOLDS: permission error; control succeeded |
| C12 | A | A's valid token | truncate AB | refused | POST /channels/glow-match/{AB}/truncate | 403 / code 17 | server replay POST -> 201 | HOLDS: permission error; control succeeded |
| C13 | A | A's valid token | delete AB | refused | DELETE /channels/glow-match/{AB} | 403 / code 17 | server replay DELETE -> 200 | HOLDS: permission error; control succeeded |

Verdict counts for 85 cases: HOLDS 68; HOLDS (filtered, not refused) 4; HOLDS (accepted, not applied) 3; INCONCLUSIVE 9; FAIL 1.

### Findings

**1. S15: a member's own membership data reaches the other member. FAIL, not closable through configuration; design blocker.**

- A's client sent `PATCH /channels/glow-match/{AB}/member` (`updateMemberPartial`) with `set: {glow_note: "<free text>"}`, and Stream answered `200`.
- Under the final configuration, where members have `read-channel` only, B received the text in its ordinary channel query (`POST /channels/glow-match/{AB}/query`, 201), inside the members list.
- The realtime path is unproven (corrected in P06.1-C1). The events view found the text because the harness recorded the SDK's local `channels.queried` event, raised by B's own query with the queried state, as if Stream had delivered it; it could not show which event, if any, Stream delivered. The recorded verdict row still reads "B read it via channel_query, B read it via events", as the harness wrote it. The channel query alone confirms S15, and I2a maps the event types.
- Only B's `GET /members` was refused (`403`, code 17).
- In the control, `read-channel-members` was granted on AB for a moment. B then also found the text through `GET /members`.
- In run 2, under v2, the same write succeeded.
- No Stream permission governs a member's update of its own membership:
  - Stream's permissions reference lists no such action. The claim that "the live permission list" has none has no recorded source: no I1 commit reads `/permissions`, and the reference is not exhaustive (corrected in P06.1-C1);
  - with `update-channel-members` removed for every role, the write still succeeded.
- Stream's [channel members documentation](https://getstream.io/chat/docs/javascript/channel-members/) allows up to 5 KB of member custom data.
- A member cannot change its own channel role this way. E6 was refused, `403` code 17 "this channel role can only be updated server side".
- Taking away `read-channel-members` (v3) did not close the channel, because the channel query still carries member data. Whether events carry it is unproven (corrected in P06.1-C1).
- Per the prompt, this line of work stopped here and is reported as a design blocker. The design or the provider path needs a decision. Possible directions are for the manager, and none was tested:
  - an app that never renders Stream member data;
  - server-side scrubbing of member custom data through webhooks, which would act after the fact;
  - a different provider.

**2. Typing events carried free text (smoke run). Closed by configuration.**

- With `typing_events` on, A sent `sendEvent({type: "typing.start", glow_text: "<free text>", text: "<free text>"})`, and Stream answered `201`.
- B received a `typing.start` event with keys `channel_id`, `channel_last_message_at`, `channel_type`, `cid`, `created_at`, `glow_text`, `received_at`, `text`, `type` and `user`. `glow_text` and `text` held A's free text.
- No permission governs typing events, so v2 turned them off.
- In the final run, the same request was refused `400` code 18 ("Event is not supported"), and B, still listening, received nothing (RT2).

### What typing and read events can carry

- **Typing:** off. With typing on, the event carries any custom field the client adds (finding 2).
- **Read:** on. A's `markRead({glow_text: "<free text>", text: "<free text>"})` was accepted with 201. B's `message.read` event carried only `channel_id`, `channel_member_count`, `channel_type`, `cid`, `created_at`, `last_read_message_id`, `received_at`, `type` and `user`. Stream dropped the custom fields (RT3). The only client-chosen value that reaches B is which message ID A marks as read.

### What A can learn about X and D

A, a member of AB only, holds X's and D's IDs, XD's channel ID and XD's message ID, as a modified client might. With those it learned no data about X, D or XD:

| Case | What A sent | What came back |
|---|---|---|
| R1, R2 | Watch or query XD | `403` code 17 |
| R3, R4, R5 | Query channels by X's membership, by D's membership, and by XD's cid | `403` code 70 "no access to requested channels", with no data |
| R6 | Fetch XD's message by ID | `403` code 17 |
| R7a | Search for XD's message text restricted to XD's cid | `400` code 4 "There are no searchable channels" |
| R7b | The same search across the whole type | `200` with no results |
| R8a, R8b | Query X and D by ID, or everyone with role `user` | `200` with zero users |
| R9 | Query XD's members | `403` code 17 |
| T4-rest-xd | Query XD claiming to be X | `403` code 17 |
| RT1 | Stay connected while XD received a message | No XD event arrived |

Existence signals remain, **not tested further**:

- A code 70 or code 17 refusal for an ID that exists may differ from the answer for an ID that does not. For example, "X has at least one channel" or "this message ID exists" might be distinguishable. The proof did not send the non-existent-ID comparison requests, so whether a real oracle exists is unverified.
- Using it requires already knowing the other person's Stream identifiers.

### Inconclusive cases, as recorded, with analysis

The harness verdicts above stand as recorded. The notes below add analysis from other retained evidence; they do not change the verdicts.

- **G1-create.**
  - The client's `POST /guest` was refused `403` code 17: "guest user creation is disabled for this application".
  - For the control, guest creation was enabled for a moment and the identical client request repeated. That request created a guest user, as Stream's user list showed at 03:29:12: ID `guest-<uuid>-p061i1-0925032853-guest`, role `guest`.
  - The SDK call as a whole still reported `403` code 17, because `setGuestUser` then connects with the guest's profile fields, which the lockdown refuses (as in S14).
  - The harness judged the control by the whole call, so it recorded INCONCLUSIVE. The request itself was well formed.
  - The harness has since been changed to judge the `POST /guest` result (see "Deviations").
- **G2-read-ab, G2-channels, G2-users, G2-message.** Not run: they needed the control's guest session, which the lockdown refused as described. The guest-role reach is therefore **untested**. Client-side guest creation is refused, so a client cannot obtain a guest.
- **G3-channels.** The anonymous client's `queryChannels({type: "glow-match"})` was refused `403` code 70 with no data. A's identical request is also refused with code 70, because the filter matches XD. So the control could not succeed. The harness now uses a filter on A's own membership, which is untested live.
- **R7a.** A received `400` code 4 "There are no searchable channels" and no data. X's identical request found the message. The refusal is not a permission code, so it does not count under the rule.
- **R9.** A's members query was refused `403` code 17. The control, X querying its own channel's members, was also refused, because no client may read member lists under v3. The harness now uses a server replay, which is untested live.
- **S10 (vote on a poll).** `polls` was enabled on the type (PUT answered `201`), and the server created a poll (`201`). The server's message attaching the poll to AB was refused `403` code 17 "polls not enabled for this channel". So no poll message could exist in AB, and no vote target existed. Polls were then turned off again and verified. Why the type change did not reach AB within 3 seconds is not known. Poll creation itself (S9) was refused `403` code 17.

### Usage and guardrails

Counted by the harness ledger (`.work/usage-ledger.json`), for the whole session:

| Resource | Used | Guardrail |
|---|---|---|
| Synthetic users | 19, conservative. Four runs of 4, plus 2 reserved guest attempts in the lost run, plus the final run's guest. The ledger said 18 until the uncounted guest was added by hand | 20 |
| Channels | 28 (four runs: 4 + 8 + 8 + 8) | 30 |
| Peak concurrent connections | 5 | 10 |
| WebSocket connection attempts | 46 | — |
| API calls | 884: 547 server, 337 client. Final run alone: 256 | 5,000 |

- No response suggested a charge, an upgrade or an exceeded limit. There was no HTTP 402 or 429 and no Stream code 9 or 99.
- The plan and usage pages were not opened; plan economics belong to P06.1-I2.
- The remaining budget allows no further full run in this session.

### Cleanup

Every run hard-deleted its channels (`POST /api/v2/chat/channels/delete`, `hard_delete: true`) and its users (`POST /api/v2/users/delete` with user, messages and conversations all `hard`), waited for both tasks to complete, and re-listed the application.

- A hard delete makes Stream create a system user, `deleted-user-1729640-<hash>` (the same ID each time), to own orphaned references. Stream's user documentation describes such a system-generated owner. From run 2 on, cleanup deleted it too. After the smoke run it was deleted by hand.
- **Final run gap.** The control's guest user was stored as `guest-<uuid>-<requested id>`. Cleanup matched run users by exact or leading prefix, so it missed this one. Verification showed "other users present: 2" but no proof users.
  - The guest was hard-deleted by hand, and that re-created the system user, which was deleted again.
  - Verification then showed 1 user (the dashboard user), 0 channels, 0 proof users and 0 system users.
  - `verify-clean` at 03:32 confirmed it: no proof users, no channels, 1 other user.
- Stream's polls and user groups created by controls were deleted explicitly: DELETE `200`. Files uploaded by controls were deleted right after upload: `200`.
- The harness now matches the run prefix anywhere in a user ID and reads the created guest's ID from Stream's response (see "Deviations").

The settings and the v3 channel-type configuration remain in place for P06.1-I2.

### Checks

All checks ran from `proofs/stream-chat/` unless noted. The results below are for the session's final tree.

| # | Check | Result |
|---|---|---|
| 1 | `git diff --check 0f45e648099b415217938c25d7369164c0101def HEAD` (repository root) | Clean, exit 0, on the final head. An earlier commit had one trailing blank line in this file, fixed before the final commit |
| 1 | `git diff --name-only 0f45e648… HEAD` | 37 paths: this file and 36 under `proofs/stream-chat/`. All owned paths |
| 2 | Trusted-base classification: `scripts/change_scope.py` from `0f45e648…` (equal to `origin/main`) extracted to a scratch directory, then `python3 -I … --base 0f45e648… --head <head> --merge-base` (system Python 3.11.15) | `{"full": true, "reason": "behavior-or-empty", …}`, exit 0. One merge base. Full scope, as expected |
| 3 | `python3.12 -m venv .venv`, then `pip install --require-hashes -r requirements-dev.lock`, then `pip check`, from a deleted `.venv` | Installed. "No broken requirements found." `getstream` 6.1.0, Ruff 0.16.8, mypy 2.3.1 |
| 3 | `npm ci --ignore-scripts`, with the proxy and CA variables passed by reference, from a deleted `node_modules` | "added 51 packages, and audited 52 packages"; "found 0 vulnerabilities". `stream-chat` 9.53.0 |
| 4 | `env -i PATH="$PATH" HOME="$HOME" LANG=C.UTF-8 .venv/bin/python -m unittest discover -s tests -t . -v` | `Ran 49 tests`, `OK`. The tests assert that no `STREAM_*` variable is present and that network connections are refused |
| 4 | `.venv/bin/ruff check .` / `.venv/bin/ruff format --check .` | "All checks passed!" / "25 files already formatted" |
| 4 | `.venv/bin/mypy` (strict; `glow_stream_proof` and `tests`) | "Success: no issues found in 25 source files" |
| 4 | `node --check client/runner.cjs` | Exit 0 |
| 5 | Live run `python -m glow_stream_proof run --accept-dashboard-user` | Final run `p061i1-0925032853`, 03:28:53–03:30:32 UTC, exit 0, tables above. Earlier runs are in "Live runs" |
| 6 | Post-run cleanup: `python -m glow_stream_proof verify-clean` at 03:32 UTC | "proof users remaining: []", "channels remaining: []", "other users present: 1" (the dashboard user), exit 0. `configure` (dry run) showed "differences before: []" |

Not run: the repository's Foundation CI jobs. None of them runs this harness's tests, and it is not part of the application, the API artifact or the Docker context, whose `.dockerignore` is an allowlist.

### Deviations from the prompt

- **Stop condition.** A user the proof did not create was present. The session stopped before any change and asked Nathan, and proceeded only on his answer (see "Stop condition").
- **Session guardrail.** The brief sets its guardrails per session; the prompt says to count per run. The harness enforces both, keeping a session-wide ledger. That ledger is what ruled out a fifth run.
- **Configuration changed between runs, from evidence.** Typing events were turned off after the smoke run, and `read-channel-members` was removed after run 2. The final configuration therefore differs from the first one. Each change is recorded above with the observation that caused it.
- **Temporary setting changes inside runs.** Channel-level feature overrides, the type-level custom-events and polls toggles, and the guest-creation toggle were added for attributable permission-layer evidence and positive controls. Each was reversed in the run; only the type toggles and the guest setting were re-read, not the channel-override removals (corrected in P06.1-C1).
- **A run's results were lost.** In run `p061i1-0925031802` an exception escaped before the results were written. The harness then wrote a progress file after every case, and the results after any `Exception`, but not after Ctrl-C (`KeyboardInterrupt`), which escaped before they were written (corrected in P06.1-C1; since P06.1-C1 Ctrl-C is handled too, except a second Ctrl-C inside the end of the run, which still lost the results file until P06.1-C2 (corrected in P06.1-C2)).
- **Cleanup missed a guest user in the final run.** It was removed by hand and verified, and the harness was fixed. The fixes in commit 5c91e3a and later have **not been exercised live**, because the session's user budget is spent (19 of 20). They are:
  - matching the run prefix anywhere in a user ID;
  - judging G1's control by its `POST /guest` result;
  - a server-replay control for R9;
  - a membership filter for the guest and anonymous channel probes.
  The offline simulation exercised them against fakes only. Its fake guest connected successfully, which masked that the lockdown refuses the connect `setGuestUser` makes, so it could not show that G2 cannot run as written; S10's procedure was unchanged (corrected in P06.1-C1). The exact-head review's run 2 was their first live use.
- **Extra dependencies.** The client pins `ws` and `https-proxy-agent`, the versions already in `stream-chat`'s dependency tree, so the SDK's WebSocket can use the session proxy. The proxy passed the WebSocket upgrade: connect, events, disconnect and reconnect all worked. Every realtime case is verified, not marked unverified.
- **Committed baseline record.** `proofs/stream-chat/baseline/application-1729640-2026-09-25.json` records the pre-proof configuration for restoring. It holds no user data.

### Limits

- The results cover application 1729640, its Free Chat plan, the `stream-chat` 9.53.0 and `getstream` 6.1.0 SDKs, and synthetic users, on 25 September 2026 between 02:51 and 03:33 UTC. Stream can change server behavior without an SDK change.
- The client matrix uses the JavaScript SDK and the REST paths it calls, plus the WebSocket. Other endpoints, including other SDKs' v2 client endpoints, were not enumerated.
- Video calls, feeds and other Stream products reachable with the same user token were neither tested nor configured.
- The guest-role reach (G2) was not run. The poll vote (S10) could not be set up.
- The existence signals described above were not tested further.
- The restore command was not executed.
- Revocation, history, outage, economics and cross-device behavior belong to P06.1-I2. Real persistence and races belong to P11.
- Added in P06.1-C1 (corrected in P06.1-C1):
  - the client processes are isolated by their environment only; they run as the same operating-system user as the server process;
  - `verify-clean` cannot see soft-deleted channels, and C13's control soft-deletes AB before cleanup;
  - at I1's head, the charge-signal check missed the typed SDK calls such as `upsert_users` and `send_message` (fixed in P06.1-C1);
  - the client endpoints in the review's finding 9 were never tried.

### Open questions for the manager

1. **S15, member custom data (design blocker).** Is exposure of membership custom data acceptable if the app never renders it, or is a design or provider change needed? No configuration closed it.
2. **Other Stream products.** Should Video (for example a call that rings B) and Feeds be assessed and locked before P06.2? Stream says one user token works for every product in the application.
3. **Guest reach and poll voting.** Should P06.1-I2 rerun G2 and S10 with the corrected harness? A new session starts with a fresh budget.
4. **Existence signals.** Should the Stream user IDs used in production be unguessable and never shown to non-matched users? This would make any existence oracle hard to use.

### Manager verification (App Manager 3, 25 September 2026)

App Manager 3 checked the relayed report against the pushed branch. The manager makes no call to Stream, so the live results above remain the session's record, backed by the harness code. The exact-head review may confirm S15 live.

- **Identity:**
  - branch `claude/compassionate-lamport-531vtk`, head `9ff600fea99cd17e6410b773a618281cc1a79b6b`, tree `0a0f05ba7409761aac55d22fb9e83b3e28defae5`;
  - the start `0f45e64…` is an ancestor of the head and its only merge base with `main`;
  - five commits, 37 files and 9,961 insertions, all in owned paths;
  - every file is new with mode 100644, and `git diff --check` is clean.
- **Classification:** the trusted policy from `main` (`0f45e64`), run outside the tree with `python3 -I`, printed `{"full": true, "reason": "behavior-or-empty", …}`. There is one merge base.
- **Secrets and personal data:**
  - the diff contains no live secret value, no JWT-shaped string and no email address;
  - the baseline JSON holds only settings, grants and channel types, with no user data, and its URL fields are empty;
  - the dashboard user's identifier and name fields appear nowhere.
- **Offline re-run.** The tree was extracted to a scratch directory and checked at about 07:50 UTC, in clean processes without any `STREAM_*` variable. Installs got the proxy and CA variables by reference.
  - `python3.12 -m venv .venv`, then `pip install --only-binary :all: --require-hashes -r requirements-dev.lock`: installed. `pip check`: "No broken requirements found." `getstream` 6.1.0, Ruff 0.16.8, mypy 2.3.1.
  - `npm ci --ignore-scripts`: "found 0 vulnerabilities". `stream-chat` 9.53.0, `ws` 8.21.3, `https-proxy-agent` 5.0.1.
  - `env -i PATH="$PATH" HOME="$HOME" LANG=C.UTF-8 .venv/bin/python -m unittest discover -s tests -t .`: `Ran 49 tests`, `OK`.
  - Ruff check: "All checks passed!". Ruff format: "25 files already formatted". mypy: "Success: no issues found in 25 source files". `node --check client/runner.cjs`: exit 0.
  - The locks: 30 and 35 pins, each with SHA-256 hashes. All 51 npm packages come from `registry.npmjs.org` with SHA-512 integrity. One package, `stream-chat`, declares an install script, which `--ignore-scripts` skips.
- **Code read:** the credential loader, the client environment's allowlist and the runner's refusal, redaction and the leak-checked writes, the usage ledger and the charge-signal stop, the configuration and restore plans, preflight, cleanup and the S15 procedure. The points for the review are in its prompt.
- **Integration:** fast-forwarded into the manager branch `claude/stoic-carson-66gdig` and pushed at 07:53 UTC. Draft [PR26](https://github.com/amthorn78/glow-dating-app/pull/26) carries it.
- **CI on `9ff600f`:**
  - The implementer's branch push, run [36091267791](https://github.com/amthorn78/glow-dating-app/actions/runs/36091267791), 03:39–03:46 UTC: all six jobs passed.
  - The manager branch's push, run [36109949498](https://github.com/amthorn78/glow-dating-app/actions/runs/36109949498), 07:53–07:58 UTC: all six jobs passed, and the gate log says `Application checks passed`.
  - No Foundation job runs the harness's own tests. The offline re-run above covers them.

### Exact-head review of I1 (25 September 2026)

Nathan ran the review session at max, from revision 3 of the [review prompt](../../ephemeral/2026-09-25-p06-1-i1-review-prompt.md) (records commit `516bee2`), and relayed its report. The session committed and pushed nothing. Its two live runs were on 25 September, between 19:33 and 19:38 UTC.

- **Verdict: changes required.** Two blocking findings must be fixed before P06.1-I2a runs live on this harness; findings 3 to 9 should be fixed in the same correction pass.
- **S15: confirmed live** on the exact head, and no configuration closes it. That meets ADR 0003's condition (DM-01 P4).
- **No finding changes a recorded I1 result.**

#### The report, as relayed

The session's note before its report, verbatim:

> The second-opinion pass reports several new items. Before including any of them, I'll verify its key SDK claims myself. (1) `setGuestUser` does `POST /guest` then `connectUser`. (2) A failed anonymous connect leaves `wsPromise` rejected, so later queries rethrow that error with no HTTP request. (3) `sendEvent`/`markRead` can fail locally, or no-op, without sending anything.
>
> Confirmed both second-opinion issues are real (failed anonymous connect blocks wsPromise, affecting query calls; sendEvent/markRead can fail silently), but neither impacted any recorded test result since requests were actually sent and answered in every run. I've merged the verified findings and dropped two claims that didn't hold up.

##### Verdict: changes required

**S15 is confirmed live on the exact head, and no configuration closes it.** This meets ADR 0003's condition (DM-01 P4) for choosing the display rule. No finding changes a recorded I1 result, and both of my live runs went cleanly.

Two defects must be fixed before P06.1-I2a runs live on this harness (findings 1 and 2):
- the harness can record a pass for a request Stream never refused;
- a failed restore of a temporary setting change does not stop the run.

Findings 3–9 should be fixed in the same correction pass. They cover the stop condition, validity checks, I2a's plan and coverage, and records that the S15 decision cites.

##### Identity and gates

- **Prompt:** revision 3, from commit `516bee262068229d44aacbab4c3f9cd77722b4e1`.
- **Head reviewed:** `git rev-parse HEAD` printed `9ff600fea99cd17e6410b773a618281cc1a79b6b` (detached).
  - `git merge-base --all origin/main HEAD` printed one line, `0f45e648099b415217938c25d7369164c0101def`.
  - The ancestor check printed "records build on the head".
- **Environment:** none of `DATABASE_URL`, `HD_API_KEY` or `GEO_API_KEY` present. All three `STREAM_*` variables set. Tools are in `/root/.local/bin`: node v24.19.0, npm 11.9.0, Python 3.12.14.
- **Classification:** the trusted policy from `origin/main` (`0f45e64`) was extracted to a temp directory outside the tree and run with `python3 -I … --merge-base`. Both runs exited 0.
  - `main → 9ff600f`: `{"full": true, "reason": "behavior-or-empty", "paths": [...]}`, 37 paths: the evidence record and 36 files under `proofs/stream-chat/`.
  - `9ff600f → 516bee2`: `{"full": false, "reason": "ordinary-docs-only", "paths": [...]}`, 29 Markdown paths.
- **Context, not reviewed:** the manager branch has moved on to `32bb2b5`, including non-Markdown files (`apps/mobile/rendered/onboarding.spec.ts`, `apps/mobile/src/components/ui.tsx`). This review does not cover them.

The report listed every path in both classification outputs; the manager's re-run below reproduced the same counts.

##### S15: confirmed

**Live** (run 1, below). Under the locked configuration I verified before and after the run:
- `glow-match` members hold `read-channel` only; every other role, and the `.app` grants of `user`, `guest` and `anonymous`, are empty;
- all three `member_custom_on_*` settings are `false`.

| | A's write (`updateMemberPartial`, `PATCH /channels/glow-match/{AB}/member`) | B: channel query | B: `GET /members` | B: events |
|---|---|---|---|---|
| Locked configuration | **200** | 201, **marker present** | 403 / code 17, absent | `channels.queried`, `member.updated`: marker present (see finding 4) |
| Control: `read-channel-members` granted on AB (override set 200, removed 200) | **200** | 201, present | 200, present | `channel.updated`, `channels.queried`, `member.updated`: present |

The verdict row (FAIL: B read it via channel query and events) is identical to I1's final run.

**Documentation and source.** This is Stream's current documentation, gathered in this session by a research sub-agent (no API calls), plus the installed SDKs.
- **No permission governs it.** The [permissions reference](https://getstream.io/chat/docs/python/permissions-reference/) lists AddOwnChannelMembership, RemoveOwnChannelMembership, UpdateChannelMembers, ReadChannelMembers, BanChannelMember and MuteChannel. None governs updating one's own membership, pinning or archiving.
- **Caveat:** that reference is not exhaustive. Stream names its ListPermissions API as the authoritative list, and I did not call it (section 4 does not allow it).
- **Live, the write needs no grant beyond `read-channel`,** which was A's only grant. `read-channel` cannot be removed without ending reads.
- **The channel query path needs no extra grant.** [Get Channel](https://getstream.io/chat/docs/python/get-channel/): with ReadChannel, "By default the response contains the channel, its configuration, and its members."
- **Nothing member-related to set:**
  - [channel features](https://getstream.io/chat/docs/python/channel-features/): nothing member-related;
  - [channel-level settings](https://getstream.io/chat/docs/python/channel-level-settings/), "the complete list": nothing member-related either; grant modifiers can only revoke an action, and there is none to revoke.
- **The `member_custom_on_*` settings only add exposure.** They copy member custom data into messages, typing events and mentions (REST spec). They do not affect query members or `member.updated`, and they are off.
- **`channel_hide_members_only`** is undocumented and not returned by `GET /app`, so it is absent from the baseline. Its effect is unknown; a question for Stream support.
- **`member.updated`** goes to "clients watching the channel" ([events](https://getstream.io/chat/docs/javascript/event-object/)). The REST spec defines its `member` as a full `ChannelMemberResponse` including `custom`.
- **Nothing closes S15 at the provider level while the chat stays usable:**
  - disabling the channel ends all client reads and writes;
  - a webhook revert acts after delivery;
  - the recipient asking for `members.limit: 0` and ignoring events is display-side only, consistent with the display rule;
  - blocking hides the channel.

**The procedure.**
- **Sound:**
  - the marker is unique per run and phase;
  - the channel-query and members-query views are Stream's responses to B's own requests;
  - the control shows B's reads can find the data;
  - the field is unset after each phase, and AB is hard-deleted.
- **Unsound:** the events view (finding 4). The realtime `member.updated` path that the records name is plausible from the spec, but neither I1's runs nor mine establish it. The channel-query path alone confirms S15, so this corrects the record without narrowing the exposure.

##### Findings, most severe first

**1. Blocking: some verdicts are taken from an SDK error, not from Stream's answer to the request under test.**
- **Where:** `proof_run.py:68-76` (`_status_code` prefers `reply.error`), `:986-999`, `:1039` (G1), `:1092-1105` (G3), `:1425-1450` (RT2/RT3). Found by the second-opinion pass; I verified it in the SDK source.
- **G1:** `setGuestUser` sends `POST /guest`, then connects (SDK `index.node.js:15467-15479`).
  - Suppose a client's `POST /guest` returns 201 and creates a guest, and the lockdown then refuses the guest's connect with 403/17. My run 2 control showed exactly this shape: "POST /guest 201; guest connect 403 / code 17".
  - The case then records **HOLDS** while `client_guest_user_exists_after` is true. The case exists to catch exactly this regression.
- **G3:** a failed `connectAnonymousUser` leaves `wsPromise` rejected (SDK `:14731-14755`, `:14816-14833`).
  - `channel.query`, `queryChannels` and `queryUsers` all await it (`:10748`, `:15965`, `:15768`), so the probes rethrow the connect's 403 or 401 without sending anything.
  - The probes then record HOLDS with Request "-". `_proc_anonymous` only notes the connect result.
- **RT2/RT3:**
  - `sendEvent` and `markAsReadRequest` throw locally in `_checkInitialized()` (`:9743`, `:10492`). That becomes outcome "other" and then HOLDS "refused (other)".
  - `markAsReadRequest` also returns `null` without a request when read events are off (`:10493`). That becomes HOLDS (accepted, not applied).
- **Recorded results are unaffected.** In I1's final run and my run 2, G1's own `POST /guest` got 403/17 ("guest user creation is disabled for this application"), the anonymous connect succeeded, and RT2/RT3 sent real requests.
- **Fix:**
  - take the status and code from this command's own recorded HTTP response, and treat "no response recorded" as INCONCLUSIVE;
  - make G1 FAIL whenever `_guest_created(reply)` is not `None`;
  - mark G3 INCONCLUSIVE unless the anonymous connect succeeded.

**2. Blocking: a failed restore of a temporary change does not stop the run, and some enables sit outside their `try`.**
- **Where:**
  - `run_matrix` catches `RunStopped` as a generic `Exception` and continues (`proof_run.py:533-542`);
  - `RunStopped` is raised by `_type_features_restore` (`:495-508`) and by the guest-creation restore (`:1013-1018`);
  - type-level enables happen before their `try` (`:644`, `:1138`);
  - the guest enable, 3 s sleep and session start happen before their `try` (`:1006-1009`);
  - nothing re-verifies the configuration at the end of the run, and `cli.py:188` exits 0.
- **Scenario:** say S12's or S10's restore `PUT` fails, or the re-read still shows the feature on, or guest creation does not read back as disabled.
  - The run records a "harness error" row and carries on. Cleanup never restores type features or app settings.
  - `glow-match` is left with `custom_events` or `polls` on, or the application with guest creation enabled. Only the next preflight or `configure` dry run would reveal it.
  - A `RunStopped` raised in a `finally` also replaces an in-flight `GuardrailStop`, so a charge signal could be swallowed.
  - A timeout or Ctrl-C between the enabling request and the `try` skips the restore entirely.
- **Fix:**
  - re-raise `RunStopped` as `GuardrailStop` is re-raised;
  - open each `try` before the enabling request;
  - keep a journal of temporary changes, and restore and verify them in `cmd_run`'s `finally`;
  - end every run with `configuration.verify()`, exiting non-zero on any difference.

**3. Should fix: preflight accepts any number of dashboard-flagged administrators.**
- **Where:** `proof_run.py:215-227`.
- **Scenario:** with `--accept-dashboard-user`, every user with role `admin` and `custom.dashboard_user` true is accepted. The count is returned but never compared with 1, and nothing pins the user Nathan confirmed.
  - A second dashboard user, or any server-created user with that flag, is accepted silently. That is wider than Nathan's direction.
  - Evidence line 91 ("accepts exactly that dashboard user") and README line 103 ("the one … user") overstate the code.
- **Fix:** stop unless exactly one such user exists. Optionally also check its `created_at` (24 September 13:07 UTC, already in the evidence); this records no identifier.

**4. Should fix: S15's events view cannot show which event carried the marker.**
- **Where:** `proof_run.py:1237`, `:1243-1244`, with `client/runner.cjs:140-143`.
- **Scenario:** `channel.query()` raises a local `channels.queried` event carrying the full queried state (SDK `:10747`, `:10823-10829`), and the runner records every event.
  - B's query runs before the events are collected, so `events_have_marker` is always true once the query carries the marker.
  - The evidence (lines 26 and 352-354), ADR 0003's Context and the brief's "S15: decided" state that B received the text in `member.updated` events. That part is unproven.
- **Fix:** exclude the SDK's local event types (for example `channels.queried`, `capabilities.changed`, `connection.changed`, `message.read_locally`) and report which event type carried the marker. Then correct the records.

**5. Should fix: replies are not matched to commands.**
- **Where:** `client_bridge.py:128-164`. `send()` never compares `raw["id"]` with the command's id.
- **Scenario:** after a 60 s timeout the session stays in use, and the late reply is read as the next command's reply.
  - Later cases are then judged on the previous request. Their server replay targets the previous case's failing record, so a HOLDS can land on the wrong request.
  - A second line already buffered in the text reader is also invisible to `select()`, so a desynchronized session can time out spuriously.
  - No timeout occurred in the recorded runs.
- **Fix:** check the reply id. On a mismatch or timeout, kill the session and mark the affected cases INCONCLUSIVE.

**6. Should fix: the plan to rerun G2 (guest reach) and S10 (poll vote) in I2a will fail as written.**
- **Where:** `proof_run.py:981-982`, `:1031-1033`, `:1080-1090`; `tests/test_run_simulation.py:135-145`.
- **G2:** the control's guest session is created by `setGuestUser({id, name})`, which connects with the guest's profile.
  - The lockdown refuses that connect, so every G2 case records "not run". My run 2 confirmed this with the corrected harness.
  - The simulation's fake guest connects successfully, which masks it. The evidence's "the offline simulation test covers them" (line 480) and the brief's "Reruns: G2 and S10 with the corrected harness" are not achievable.
- **S10:** its procedure is unchanged, and its type-level toggle did not reach AB within 3 s in I1's run.
- **Fix, in I2a's prompt:**
  - G2: create the guest server-side with the unused `ServerApi.create_guest` (`server_api.py:144-160`) and connect with `{id}` only;
  - S10: design a new setup.

**7. Should fix: the leak terms for G2/G3 `read-ab` and `message` cover message text only.**
- **Where:** `matrix.py:332-337`, used at `proof_run.py:1106-1107` and `:1121-1123`.
- **Scenario:** a guest or anonymous 2xx that returned AB's channel object, members, names or message ids, but no text, would record HOLDS (filtered, not refused). Recorded G3 results were refusals, so they are unaffected.
- **Fix:**
  - `read-ab`: add `{AB}`, `{A}`, `{B}`, `{A_name}`, `{B_name}`, `{m_a}` and `{m_b}`;
  - `message`: add `{m_x}`, `{X}` and `{XD}`.

**8. Should fix: claims in the records that the code or results do not support.**
- **Evidence line 17** says every out-of-design action got "403 … and the positive control succeeded each time". Its own rows contradict that: 9 INCONCLUSIVE, S15 got 200, RT3 got 201, and the filtered cases got 200.
- **"From Stream's permission layer" also overreads code 17.**
  - Stream documents 403 "Not Allowed" for disabled and frozen channels.
  - Code 17 was also observed for "polls not enabled", "guest user creation is disabled" and "channel role can only be updated server side".
  - Attribution rests on the controls.
- **The HOLDS legend** (lines 217-221) does not cover RT1 (no refusal at all), RT2 (400/18) or RT3 (201).
- **Line 144** and README line 137 say temporary changes were "reversed and verified". Channel-override removals are never re-read, and finding 2 applies.
- **Line 359**, "the live permission list has no such action", has no recorded source: no I1 commit ever reads `/permissions`.
- **Line 474** says results are written "on any error". That does not hold for a KeyboardInterrupt (`cli.py:170-185`); the per-case progress file does exist.
- **The G3-channels action text** "empty filter" (`matrix.py:334`) is stale. I1's final run used a type filter, and the code now filters on A's membership.
- **The `Limits` section is missing:**
  - the client is isolated by its environment only, running under the same user;
  - verify-clean cannot see soft-deleted channels;
  - charge detection does not cover typed SDK calls;
  - the endpoints in finding 9 were never tried.

**9. Should fix, in I2a's scope: client-reachable endpoints the matrix never tried.** Line numbers are in `stream-chat` 9.53.0.
- **Content or effect in front of B:**
  - `channel.updateAIState(…, {ai_message})` (`:10411`) sends `ai_indicator.update` with free text. Stream calls these custom events but does not say whether `custom_events` gates them.
  - The deprecated `channel.partialUpdateMember(B, …)` writes to B's membership (`PATCH …/member/{user_id}`, `:9842`).
  - `pin()` and `archive()` (`:10327`, `:10285`) set `pinned` or `archived` on A's own membership, which the spec says reaches B.
  - Invites: `inviteMembers` (`:10196`), and `acceptInvite` or `rejectInvite` with a system `message` (`:10120`, `:10130`).
  - A leaving AB with a message.
  - `banUser` or `shadowBan` of B in AB (`:10847`, `:10904`).
- **Reading outside the match:**
  - `client.sync([XD_cid], …)` (`:17391`);
  - `getReplies`, `getReactions` and `getMessagesById` on XD (`:10617`, `:10658`, `:10673`);
  - `queryReactions` (`:16053`), `getThread` (`:17129`) and `queryMessageHistory` (`:18214`) on XD's message.
- **Required cases still weaker than required:** G2 and S10 never ran, and R7a is inconclusive.

**Nits**
1. RT2/RT3 look for the marker only in the named event types and the first window (`proof_run.py:1427-1434`).
2. `AUTH_CODES` includes code 2, which Stream documents as an API-key error, not a token refusal (`matrix.py:32`).
3. The `?user_id={X}` and `{B}` suffixes are hard-coded (`:911`, `:970`) rather than read from the recorded parameters. The SDK does send them.
4. Undo and override-removal results are never checked (`:611-614`, `:640-641`, `:713-714`, `:1283-1284`).
5. Cleanup is one unguarded sequence, and its task statuses are not asserted. `cmd_run` exits 0 whatever cleanup finds (`cli.py:188`).
6. The charge-signal check misses typed SDK calls such as `upsert_users` and `send_message` (`server_api.py:124-126`).
7. The unused runner op `request` passes `{params}` as POST's `config`, which overwrites the SDK's `api_key` and `user_id` (`runner.cjs:278-283`).
8. `cmd_baseline` writes the raw snapshot to `.work/`, including every user (the dashboard user's identifier and name fields too) and the full app object (`cli.py:86-88`). Redaction matches exact key names only.
9. `configuration.verify` checks neither `permission_version` nor the three `member_custom_on_*` settings (`configuration.py:207-244`).
10. `restore --apply` does not re-read and verify (`cli.py:232-240`).
11. Nothing asserts that `stream-chat` loads the same `isomorphic-ws` module the runner replaces (`runner.cjs:47-55`).
12. `CLEANUP_RESERVE` (60 calls) is below cleanup's worst case of about 100 calls (`proof_run.py:33`).
13. A poll or user group a client creates in a FAIL case is never cleaned up, and verify-clean lists neither.
14. verify-clean cannot see soft-deleted channels, and C13's control soft-deletes AB before cleanup.
15. `_check` stores its evidence text unredacted (`:164-166`, `:452`). A token-shaped string would make later writes fail and lose the results; it would not leak.
16. E5 and S14 judge only the stored state (`connect_me_role` is recorded but unused). T4-rest-unread records HOLDS on a refusal without its controls (`:955-956`).
17. Cleanup hard-deletes the application-wide `deleted-user-1729640-…` user. That is safe here only because preflight guarantees no other data.

##### Areas reviewed with no findings

- **Credential loading:** refuses when an HDE variable is present (checked by name), pins application 1729640 and keeps the secret out of `repr`.
- **Client isolation:** the client environment is built from an allowlist and refuses the secret's name or value; the runner exits 3 if the name is present. The only subprocess is `node client/runner.cjs`.
- **Output paths:**
  - every print is redacted and leak-checked, and every `.work` file is leak-checked;
  - the WebSocket URL (which carries the token) is never recorded, the SDK logger is a no-op, and insights are off;
  - `access_token` is redacted by key and by pattern;
  - `getstream` logs only a message name at WARNING level or above;
  - Node keeps tokens on one line, so the line-by-line redactor holds.
- **Tokens:** 900 s tokens (905 s with the SDK's 5 s back-dating). The authorized path passed 18 of 18 checks in both my runs.
- **Configuration:**
  - `apply_plan` and `verify` match the README and the evidence;
  - the live state today matches the evidence: only `guest_user_creation_disabled` differs from the baseline, and every recorded feature and command of the default types is unchanged;
  - so the restore plan's inputs would return the recorded settings. Fields the baseline does not record were not compared.
  - The emptied admin role affects only client-side sessions of admin, moderator or global roles; server-side calls bypass permission checks.
- **Matrix logic:**
  - the feature-phase cases S2, S5, S6, S7 and S12 are sound, because the control runs under the same override;
  - the T4 identity checks are sound: `me.id` comes from the handshake, and the SDK sends the claimed `user_id` on REST calls;
  - the claim that commits after `ed162e1` changed only the four fixes, the text and the simulation is accurate.
- **Dependencies:**
  - locks: 30 and 35 pins, every one with SHA-256 hashes, and no index or editable directives;
  - npm: 51 packages from `registry.npmjs.org` with SHA-512 integrity; only `stream-chat` has an install script (a Husky `postinstall`), which `--ignore-scripts` skips; no nested packages;
  - `ws` 8.21.3 and `https-proxy-agent` 5.0.1 are pinned;
  - nothing weakens TLS; `allowServerSideConnect` only silences an SDK warning;
  - `stream-chat` 9.53.0 is npm's `latest` (published 15 September 2026).
- **Scope:**
  - only `proofs/stream-chat/**` and the evidence record changed;
  - no application runtime, CI, configuration, `.env.example`, `.claude/` or `GLOW_*` change;
  - every file is new with mode 100644, and there are no symlinks.

##### Checks run

1. **`git diff --check origin/main...HEAD`:** no output, exit 0.
2. **Classifications:** both as above.
3. **Installs** (in `env -i`, with the proxy and CA variables passed by reference):
   - `python3.12 -m venv .venv` → Python 3.12.14;
   - `pip install --require-hashes -r requirements-dev.lock` → 35 packages installed, including `getstream` 6.1.0, Ruff 0.16.8 and mypy 2.3.1;
   - `pip check` → "No broken requirements found.";
   - `npm ci --ignore-scripts` → "added 51 packages, and audited 52 packages", "found 0 vulnerabilities".
4. **Offline checks:**
   - unittest: "Ran 49 tests", "OK";
   - `ruff check .`: "All checks passed!";
   - `ruff format --check .`: "25 files already formatted";
   - `mypy`: "Success: no issues found in 25 source files";
   - `node --check client/runner.cjs`: exit 0.
5. **Secret scan:**
   - the whole diff (476,116 bytes): the secret 0 times, JWT-shaped strings 0, the API key 0; no email addresses, key shapes or TLS-weakening settings;
   - every identifier-like string in the evidence, baseline and README is synthetic or already known;
   - every live output and `.work` file: the secret, its first 16 characters, JWTs, payload-and-signature fragments and the API key all 0.
6. **Live runs:** below.
7. **Also:**
   - read the relevant SDK sources;
   - compared the live state with the baseline;
   - diffed the harness from `ed162e1` to `9ff600f`;
   - checked the engines against `scripts/bootstrap-toolchain.sh`.

##### Live runs (25 September 2026, UTC; one checkout, one command at a time)

- **Before any run:**
  - `verify-clean` (19:33:30): "proof users remaining: []", "channels remaining: []", "other users present: 1".
  - Dry-run `configure` (19:33:38): "differences before: []".
  - Counts: 1 dashboard administrator, 0 `deleted-user` users.
- **Run 1:** `run --accept-dashboard-user --only S15`, prefix `p061i1-0925193403`, 19:34:03 to 19:34:35, exit 0.
  - Authorized path 18 of 18 PASS; S15 FAIL (above).
  - Usage: 4 users, 2 channels, 47 API calls (35 server, 12 client), a peak of 3 connections.
  - Cleanup: channels and users deleted (201, tasks completed), 1 `deleted-user` artifact deleted, nothing remaining.
- **Run 2:** `run --accept-dashboard-user --only G1-create,G2-read-ab,G2-channels,G2-users,G2-message,G3-read-ab,G3-channels,G3-users,G3-message,R9`, prefix `p061i1-0925193620`, 19:36:20 to 19:36:53, exit 0.
  - Authorized path 18 of 18 PASS.
  - G1-create HOLDS: A's `POST /guest` got 403/17. In the control, guest creation was enabled for about 5 s, `POST /guest` got 201, the guest connect got 403/17, and creation was disabled again and verified.
  - G2 × 4 INCONCLUSIVE ("not run: no guest session").
  - G3-read-ab HOLDS (403/17). G3-channels HOLDS (403/70). G3-users HOLDS, filtered (200). G3-message HOLDS (403/17).
  - R9 HOLDS: 403/17, "not allowed to perform action ReadChannel", with the server replay getting 200.
  - Usage: 5 users, 2 channels, 52 API calls (36 server, 16 client), a peak of 4 connections.
  - Cleanup: the Stream-prefixed guest was deleted by the ID Stream returned; 1 artifact deleted; nothing remaining.
- **After the last run:**
  - `verify-clean` (19:37:21): `[]`, `[]`, 1.
  - Dry-run `configure` (19:37:23): "differences before: []".
  - Before and after compared field by field (app settings, client-role grants, all six channel types including `updated_at`): identical.
- **First live use of the fixes:** the four post-run fixes (cleanup's run-prefix matching and guest-ID capture, the G1 `POST /guest` judgement, the R9 server replay, and the membership filter for the guest and anonymous channel probes) all worked. Cleanup and `verify-clean` behaved as intended.
- **Session totals:** 9 of 20 users, 4 of 30 channels, 119 of 5,000 API calls, a peak of 4 of 10 connections. Nothing suggested a charge.

##### Limits

- **Permissions list:** I did not call the ListPermissions API; section 4 does not allow it.
- **Case coverage:** of the 85 cases, I re-ran 11 live (S15 and the ten in run 2). The rest I checked by code path, because I1's `.work` output is not in the repository.
- **Not verified:** `member.updated` content (finding 4); the restore plan, which I did not execute; channel-type fields the baseline does not record.
- **Dashboard user's fields:** checked only by proxy. I did not read that user's details, per Nathan's direction.
- **Sub-agents:** the documentation research was done by a sub-agent. A second, read-only sub-agent did an independent code pass; I verified every item I took from it. Neither made any Stream call.
- **Hosted CI:** not checked, as the prompt allows.
- **Instrumentation:** I ran the dry-run `configure` through a wrapper (identical Stream calls) that saved channel types and app settings, with no user data, to my scratchpad. The harness itself was started through a launcher with an allowlisted environment, so no value appeared in a process argument.
- **Temporary in-run changes:** both runs made the harness's own temporary changes (AB's override in run 1; the guest-creation toggle in run 2). Each was restored and verified, and the final configuration is identical.
- **Repository:** nothing committed or pushed; only ignored files were created.

#### Manager verification of the review (App Manager 3, 26 September 2026)

The session committed nothing, so there is no branch to check. The manager checked the report's claims against the reviewed head and the SDK source. The manager makes no call to Stream, so the live runs above are the session's record.

- **Identity.** The manager re-ran both classifications with the trusted `main` policy (`0f45e64`), outside the tree, with `python3 -I` and `--merge-base`:
  - `main → 9ff600f`: full scope (`behavior-or-empty`), 37 paths;
  - `9ff600f → 516bee2`: `ordinary-docs-only`, 29 paths.

  `0f45e64` is the only merge base, and `516bee2` builds on `9ff600f`.
- **SDK claims,** in `stream-chat` 9.53.0's `dist/cjs/index.node.js` (20,040 lines), from the manager's offline install from the lock:
  - `setGuestUser` posts `/guest` and then calls `connectUser` (15467–15479);
  - `connectAnonymousUser` returns `_setupConnection()`, which is `openConnection`. That binds `wsPromise` to the connect through `_bindWsPromise`, so a failed connect rejects it (14711, 14731–14755, 14762, 14816–14833);
  - `channel.query`, `queryUsers` and `queryChannels` each await `wsPromise` first (10748, 15768, 15965);
  - `sendEvent` and `markAsReadRequest` call `_checkInitialized()`, which throws on a client for a channel not yet initialized (9743, 10492). `markAsReadRequest` returns `null` without a request when read events are off (10493–10495);
  - `channel.query` dispatches a local `channels.queried` event with the queried state (10823–10829).
- **Harness claims at `9ff600f`:**
  - **Finding 1:** `_status_code` uses the reply's own status and code before any recorded response (`proof_run.py:68-76`). G1's verdict is `refused_verdict(outcome, control_ok)` whatever `exists_after` says (`:994-999`, `:1039`). `_proc_anonymous` notes the connect result and probes anyway (`:1092-1099`). `_payload_case` turns a local throw into a refusal, and a `null` into an accepted request (`:1422-1450`).
  - **Finding 2:** `RunStopped` and `GuardrailStop` are separate `RuntimeError` subclasses (`proof_run.py:40`, `usage.py:34`). `run_matrix` re-raises only `GuardrailStop` and records anything else as a harness-error row (`:533-542`). The type-feature enable comes before its `try` (`:644`), as do the guest enable, the sleep and the session start (`:1006-1009`). `cmd_run` returns 0 whenever no stop reason was set, whatever cleanup reports (`cli.py:170-188`).
  - **Finding 3:** preflight counts dashboard-flagged administrators but never compares the count with 1 (`:215-227`).
  - **Finding 4:** `events_have_marker` searches every event B's runner recorded, after B's own query (`:1237-1244`). The runner records every event except `health.check` (`runner.cjs:140-143`).
  - **Finding 5:** `send()` never compares the reply's `id` with the command's (`client_bridge.py:128-164`).
  - **Finding 6:** `ServerApi.create_guest` exists (`server_api.py:144-160`), and nothing in the harness calls it. The simulation's fake guest connects successfully (`test_run_simulation.py:135-145`). G2 records "not run" without a guest session (`proof_run.py:1080-1090`).
  - **Finding 7:** the `read-ab` and `message` leak terms are message text only (`matrix.py:332-337`).
  - **Finding 8:** each evidence and README line it cites says what the review quotes.
  - **Nits 2, 9 and 12** as stated (`matrix.py:32`, `configuration.py:207-244`, `proof_run.py:33`).
- **Not checked by the manager:** the live runs and the documentation research. The session's before-and-after checks show the application as it was before the runs.
- **What this review covers:** code head `9ff600f` only. The flake fix at `8b8b1bd` needs its own exact-head review.

#### Disposition

- **S15 is confirmed live.** ADR 0003's condition is met, so the display rule stands as S15's answer. The realtime `member.updated` path is not established (finding 4); the channel query alone carries the text. The manager corrected ADR 0003's Context and the brief's "S15: decided" on 26 September. This record's lines 26 and 352–354 are corrected in the correction pass, with finding 4's fix.
- **Verdict: changes required.** I1's code head is not yet a sound base for I2a.
- **The correction pass, P06.1-C1.** One implementation session fixes findings 1 to 8 and the nits within its scope, and corrects the records findings 4 and 8 name; any nit it leaves gets a reason. Its own exact-head review follows. In the linear order (OD-29), it comes after the flake fix's review.
- **Into I2a's prompt:** finding 6's new G2 and S10 setups, and finding 9's endpoints.
- **For Stream support,** if Nathan chooses to ask: whether client writes to member custom data can be disabled (already recorded), and what the undocumented `channel_hide_members_only` does.
- **No recorded I1 result changes.**

## P06.1-C1 corrections

The correction pass on the I1 harness, for the exact-head review's findings 1 to 8 and its nits. It made no Stream call and ran none of the harness's live commands. The first live use of these fixes is in P06.1-I2a.

- **Prompt:** revision 1, from commit `360ad9e5cedd5084702830b092ca02ba342da686`.
- **Branch:** `claude/youthful-pasteur-caokpc`. **Start:** `360ad9e5cedd5084702830b092ca02ba342da686`.
- **Code head:** `be46319bc9e1aafdc747aca7280b2fa06a1793f9`. It carries every code change, and every check below ran on it. The commit that adds this section changes only this record.
- **Date:** 26 September 2026.

### Environment and start gate

| Check | Result |
|---|---|
| `DATABASE_URL`, `HD_API_KEY`, `GEO_API_KEY` | None present (the check printed nothing) |
| `STREAM_APP_ID`, `STREAM_API_KEY`, `STREAM_API_SECRET` | None present (the check printed nothing) |
| `command -v node npm npx python3.12` | `/root/.local/bin/node`, `/root/.local/bin/npm`, `/root/.local/bin/npx`, `/root/.local/bin/python3.12` |
| Versions | node v24.19.0; npm 11.9.0; Python 3.12.14 |
| Start gate | `git fetch origin claude/stoic-carson-66gdig`; `git merge --ff-only 360ad9e…` fast-forwarded; `git rev-parse HEAD` printed `360ad9e5cedd5084702830b092ca02ba342da686`; `git diff --stat 9ff600f… HEAD -- proofs/stream-chat/` printed nothing |

The environment was never dumped. There were no connections to Stream, a database, HDE or Railway, and no `playwright install`, `eas` or `migrate`. Installs got the proxy and CA variables by reference.

### Findings 1 to 8

Paths are under `proofs/stream-chat/`. Line numbers are at the code head. Each test below fails with its fix reverted and passes with it (see "Checks", item 5).

| Finding | Status | Where | Tests |
|---|---|---|---|
| 1. Verdicts from the request under test | Fixed | `glow_stream_proof/proof_run.py:130` `_answer_of`, `:143` `_http_answer`, `:153` `_ws_answer`; G1 `:1454`, FAIL at `:1520`; G3 `:1588`; RT2/RT3 `:2062`, no-answer rule at `:2086`; `glow_stream_proof/matrix.py:204` (`no-response` is never HOLDS); `client/error-info.cjs:42` (`ws-api` only for Stream's own error frame) | `tests/test_answers.py` (all); `tests/test_runner.py` `ErrorInfoTest` |
| 2. Restores always made; a failed restore stops the run | Fixed | journal and restore `proof_run.py:387` `_temporary`, `:410` `_restore`; `RunStopped` re-raised `:953`; enabling requests inside the journalled block (`:1059`, `:1454`, `:1639`, `:1910`); end of every run `:2356` `finish` (journal restored with retries, cleanup, `configuration.verify()`); `cli.py:142` `cmd_run` (Ctrl-C `:179`, `finish` `:187`, exit 2 or 4) | `tests/test_temporary_changes.py`; `tests/test_cli.py` (exit codes, Ctrl-C, configuration drift, cleanup problem) |
| 3. Exactly one dashboard user | Fixed | `proof_run.py:603` (exactly one) and `:608` (created in the recorded minute, 24 September 2026 13:07 UTC; constant `:63`). No identifier is read into the record | `tests/test_preflight.py` |
| 4. Events view | Fixed | `matrix.py:49` `LOCAL_EVENT_TYPES` (stream-chat 9.53.0's declared local events, plus health checks); `proof_run.py:837` `_events_split`; S15's view records the carrying event type `:1764` | `tests/test_events.py` (including a test that reads the installed SDK's `EVENT_MAP` and checks every declared local event is dropped) |
| 5. Replies matched to commands | Fixed | `glow_stream_proof/client_bridge.py:202` (id check), `:142` reader thread, `:183`, `:192`; a timeout, mismatch, non-JSON line or exit ends the session (`:156`), and its later commands raise `ClientSessionEnded` without being sent; `proof_run.py:930` records affected cases INCONCLUSIVE. (Corrected in P06.1-I2a: at its first live use, I2a's run 1, the check ended the session at the first channel command, because each command was built as `{"id": <command id>, …, **params}` and a channel command's `id` parameter, the channel, replaced the command's own; fixed in `7ce93cc`, see "P06.1-I2a") | `tests/test_client_session.py` (fake runner scripts: mismatch, timeout, two replies in one write, exit) |
| 6. Offline simulation like the live lockdown | Fixed (my part) | `tests/fakes.py:297`: the control's `POST /guest` gets 201, then its connect gets 403 / 17 | `tests/test_run_simulation.py` `test_guest_reach_is_not_run_when_the_guest_connect_is_refused` |
| 7. Leak terms | Fixed | `matrix.py:369` (`read-ab`: AB, A, B, both names, both message IDs, both texts), `:384` (`message`: XD's message ID, X, XD, the text) | `tests/test_procedures.py` `LeakTermsTest` |
| 8. Records | Corrected | See "Records corrected" | Not applicable |

Finding 6's new G2 and S10 setups, and finding 9, are I2a's work and were not built.

### Nits 1 to 17

| Nit | Status | Where | Tests |
|---|---|---|---|
| 1. RT2/RT3 search only named types and the first window | Fixed: every delivered event, of any type, in both windows | `proof_run.py:2062`, `:2073` | `tests/test_events.py` `PayloadWindowsTest` |
| 2. Code 2 counted as a token refusal | Fixed | `matrix.py:41` | `tests/test_matrix.py` `test_api_key_error_is_not_a_token_refusal` |
| 3. Hard-coded `?user_id=` suffixes | Fixed: read from the recorded request | `proof_run.py:1444` | `tests/test_procedures.py` `ClaimRequestLineTest` |
| 4. Undo and override-removal results unchecked | Fixed: every undo is checked, and a failed undo stops the run after its case is recorded (`:452`); removals are status-checked and re-read (`:467`, `:493`, `:211`) | as listed | `tests/test_temporary_changes.py` `UndoCheckTest`, `ChannelOverrideRemovalTest`, `OverrideReReadShapeTest` |
| 5. Cleanup unguarded, statuses unasserted, exit 0 | Fixed: guarded steps, deletes and task statuses judged, non-zero exit | `proof_run.py:2198`, `:2438`; `cli.py:142` | `tests/test_cleanup.py`; `tests/test_cli.py` |
| 6. Charge signal misses typed SDK calls | Fixed: an httpx response hook checks every server response | `server_api.py:97` | `tests/test_server_api.py` (on an `httpx.MockTransport`) |
| 7. Unused runner op `request` | Fixed: removed | `client/runner.cjs:260` (the op list) | `tests/test_runner.py` `test_unused_request_op_is_gone` |
| 8. `baseline` writes every user; redaction by exact key only | Fixed: the written snapshot keeps only counts and the proof's own IDs, and the settings the proof reads; credential keys are matched by pattern, but not all of them: `firebase_server_key`, `sqs_key`, `sns_key`, `server_key`, `s3_api_key`, the Datadog `api_key` and the RTMP `stream_key` in the app settings model were missed until P06.1-C2 (corrected in P06.1-C2) | `baseline.py:46`; `cli.py:86`; `redaction.py:33` | `tests/test_cli.py` `test_baseline_writes_no_other_users_identifier_or_name`; `tests/test_redaction.py` `test_sensitive_keys_are_matched_by_pattern` |
| 9. `verify` skips `permission_version` and `member_custom_on_*` | Fixed | `configuration.py:95`, `:227` | `tests/test_configuration.py` `test_verify_checks_permission_version_and_member_custom_settings` |
| 10. `restore --apply` does not verify | Fixed: re-reads and compares with the recorded baseline, exit 1 on any difference | `cli.py:255`; `configuration.py:300` | `tests/test_cli.py` `test_restore_apply_verifies_what_it_restored`; `tests/test_configuration.py` `test_verify_restored` |
| 11. Nothing asserts the shared `isomorphic-ws` | Fixed: the runner refuses to start (exit 4) unless stream-chat resolves and keeps the runner's module; a `selfcheck` op reports it | `client/runner.cjs:66`, `:218` | `tests/test_runner.py` `test_stream_chat_uses_the_runners_websocket` |
| 12. `CLEANUP_RESERVE` too low | Fixed: 130, plus a 30-call margin per case; measured worst case 115 | `proof_run.py:53` | `tests/test_cleanup.py` `CleanupReserveTest` |
| 13. Client-created polls and groups not cleaned up or listed | Fixed: tracked and deleted; verify-clean lists polls and user groups, counting only those absent at preflight. (Corrected in P06.1-I2a: at its first live use Stream refused the poll listing, HTTP 400 code 4, "either user or user_id must be provided when using server side auth", so polls are reported not verified; user groups are listed) | `proof_run.py:1161`, `:2417`, `:2345` | `tests/test_cleanup.py` `ClientCreatedDataTest`, `PreexistingPollsAndGroupsTest`; `tests/test_cli.py` `test_verify_clean_lists_polls_and_user_groups` |
| 14. verify-clean cannot see soft-deleted channels | **Left.** There is no verified way to list soft-deleted channels offline. The covering control is the hard delete of every recorded channel ID, with its task now required to report `completed` (nit 5). Recorded in the README's limits | — | — |
| 15. `_check` evidence unredacted | Fixed | `proof_run.py:340` | `tests/test_procedures.py` `CheckRedactionTest` |
| 16. E5 and S14 judge stored state only; T4-rest-unread HOLDS without its controls | Fixed: the connection's own user object in Stream's handshake counts too; the refusal needs A's and B's own requests to succeed. An accepted claim could still give HOLDS (accepted, not applied) without its controls, and an unreadable stored user made E5 a FAIL, until P06.1-C2 (corrected in P06.1-C2) | `proof_run.py:2046`, `:2003`, `:1417` | `tests/test_procedures.py` `NotEffectiveTest` |
| 17. Cleanup deletes the application-wide `deleted-user-1729640-…` user | **Left.** It is safe by construction: preflight refuses any user the run did not create except the one dashboard user, and only artifacts created after the run started are deleted. Recorded in the README's limits | — | — |

### The independent review of these corrections

A read-only sub-agent reviewed the diff at `db84220` adversarially. It made no Stream call. It found no verdict that can HOLD without Stream's refusal, no weakened rule and no credential change. It raised five points and some nits; I verified each against the code and fixed all of them in `be46319`:

1. **Override-removal re-read.** The check assumed a response shape nobody had observed live. AB is now re-read while the override is set. A later re-read proves a key's removal only if the first showed that key set. A grant the re-read cannot show is checked by B's members query being refused again. Anything else is recorded as not verified, and the run exits 4, instead of stopping. The re-reads' shape (key names only) is kept in the case detail. Tests: `OverrideReReadShapeTest`.
2. **A failed restore discarded the case's result.** The row now keeps what the case observed: a FAIL stays a FAIL, and anything else becomes INCONCLUSIVE (`proof_run.py:431`). Tests: `KeptRowTest`.
3. **An unset in S15's `finally` could replace an in-flight guardrail stop.** It no longer raises, except a guardrail stop of its own (`:1804`). Test: `GuardedUnsetTest`.
4. **Pre-existing polls and groups counted as leftovers.** Preflight lists them; only new ones count. Test: `PreexistingPollsAndGroupsTest`.
5. **One immediate restore retry.** Now three attempts, 10 s and 20 s apart, except when the call budget is spent (`:46`). Tests: `FinishRetryTest`.
6. **Nits.**
   - The runner's error classification moved to `client/error-info.cjs` and is tested offline.
   - An anonymous connect that never answered is no longer a `KeyError`.
   - `verify_restored` also checks `automod`, `automod_behavior` and `max_message_length`.
   - A code comment cited the wrong test file.

### Records corrected

In this record, each edited in place and marked "(corrected in P06.1-C1)". No recorded result changed, and the manager's sections are unchanged byte for byte.

- **Summary, outcome 1:** 65 of 85 cases, not all, held with an attributable refusal and a successful control. The other 20 are listed. Code 17 alone does not prove the permission layer; attribution rests on the controls.
- **Summary, outcome 3; finding 1's S15 lines (old 352–354); "Taking away read-channel-members":** B's channel query carries S15's text. The realtime path, including `member.updated`, is unproven: the harness counted the SDK's local `channels.queried` event. I2a maps it.
- **Stop condition (old line 91):** at I1's head the flag accepted any number of dashboard-flagged administrators. It now requires exactly one, with the recorded creation minute.
- **Temporary changes (old line 144) and the matching deviation:** only the type toggles and the guest setting were re-read. Channel-override removals were not, and a failed restore did not stop the run.
- **Verdict legend:** RT1, RT2 and RT3 are now covered.
- **G2-channels and G3-channels action text:** a type filter, not "an empty filter".
- **Finding 1's "the live permission list has no such action" (old line 359):** it has no recorded source. The claim rests on the documented permissions reference, which is not exhaustive.
- **Deviations, "results written on any error" (old line 474):** at I1's head this was not true for Ctrl-C.
- **Deviations, "the offline simulation covers them" (old line 480):** its fake guest connected, which masked G2. The review's run 2 was the fixes' first live use.
- **Limits:** added the four missing items.

In `proofs/stream-chat/README.md`:

- the dashboard-user sentence (old line 103);
- the temporary-changes claim (old line 137), now replaced by the journal and verification rules;
- a new "Verdict rules" section, with each changed rule marked;
- the end-of-run sequence and exit codes;
- the charge-signal scope, and what happens after a charge signal;
- the remedy for a restore that fails;
- the added limits.

### Checks

Run from `proofs/stream-chat/` unless noted, at code head `be46319`, in clean processes (`env -i`), with no `STREAM_*` variable present.

| # | Check | Result |
|---|---|---|
| 1 | `git diff --check 360ad9e… HEAD` (repository root) | No output, exit 0 |
| 1 | `git diff --name-only 360ad9e… HEAD` | 29 paths: this record and 28 under `proofs/stream-chat/`. All owned; no dependency file, no `pyproject.toml` change and no baseline change; every new file mode 100644, no symlink |
| 2 | The trusted policy from `origin/main` (`0f45e64`), extracted to a temporary directory outside the tree, run with system Python 3.11.15: `python3 -I change_scope.py --base 360ad9e… --head be46319… --merge-base` | Exit 0; `{"full": true, "reason": "behavior-or-empty", …}`, 29 paths. One merge base, `360ad9e…`. Full scope, as expected |
| 3 | From deleted `.venv` and `node_modules`: `python3.12 -m venv .venv`; `.venv/bin/python -m pip install --require-hashes -r requirements-dev.lock`; `pip check`; `npm ci --ignore-scripts` (proxy and CA variables by reference) | Python 3.12.14; "No broken requirements found."; `getstream` 6.1.0, Ruff 0.16.8, mypy 2.3.1; "added 51 packages, and audited 52 packages", "found 0 vulnerabilities"; `stream-chat` 9.53.0, `ws` 8.21.3, `https-proxy-agent` 5.0.1 |
| 4 | `env -i PATH="$PATH" HOME="$HOME" LANG=C.UTF-8 .venv/bin/python -m unittest discover -s tests -t . -v` | Before: `Ran 49 tests`, `OK` (at `360ad9e`). After: `Ran 142 tests`, `OK` |
| 4 | `.venv/bin/ruff check .` / `.venv/bin/ruff format --check .` | "All checks passed!" / "37 files already formatted" |
| 4 | `.venv/bin/mypy` | "Success: no issues found in 36 source files" |
| 4 | `node --check client/runner.cjs`; `node --check client/error-info.cjs` | Exit 0; exit 0 |
| 5 | `.venv/bin/python checks/fix_reversals.py`: for each fix, a scratch copy outside the tree gets that fix reverted and the fix's tests run; then the fix is put back and they run again | Exit 0; "reversals: 51, not demonstrated: 0". Every reversal's tests failed, and passed once the fix was restored. It covers every finding and nit fixed above, and the review's points. One reversal (Ctrl-C) fails by the interrupt escaping and aborting the test process, which the script counts as failing |
| 6 | Secret scan of the whole diff from `360ad9e` (301,502 bytes) | JWT-shaped strings 0; email addresses 0; key or token shapes 0; the application's API key 0; TLS-weakening settings 0; environment dumps 0 |

Not run: any live command, and the repository's Foundation CI (not triggered by this session, and it does not run this harness's tests).

### Deviations and limits

- **Decisions to confirm.**
  - After a charge-signal stop, the run still restores its journalled changes and re-reads the configuration (a few calls), but deletes none of its users or channels. The prompt required every run to restore and verify, and leaving a temporary change in place would weaken the lockdown.
  - A failed undo of a control's change stops the run after its case is recorded, because later cases would run on changed state.
  - A removal the re-read cannot show is recorded as not verified (exit 4), not treated as a stop.
- **New files beyond the harness modules:**
  - `client/error-info.cjs`, split out of the runner so that it can be tested;
  - `tests/fakes.py`, shared fakes;
  - `checks/fix_reversals.py`, which proves each fix is tested. Its reversal table quotes source lines, so it carries a file-level `ruff: noqa: E501`.
- **Not tested offline:** Stream's live response shapes. The tests prove the harness's logic against fakes.
- **Nits 14 and 17 are left,** with the reasons above.
- **No dependency change,** and nothing outside the owned paths.

### What P06.1-I2a must know

- **Not exercised live:** every fix above. That includes:
  - the answer-based verdicts;
  - the journal, restore retries and final `configuration.verify()`;
  - the one-dashboard-user preflight with its creation-minute check;
  - reply matching;
  - the local-event filter;
  - the typed-call charge hook;
  - cleanup's judgement;
  - `restore --apply`'s verification.
- **New server calls, never run live:**
  - `POST /api/v2/chat/channels` filtered by `cid` (the override re-reads);
  - `POST /api/v2/polls/query` and `GET /api/v2/usergroups` (preflight and verify-clean; paths from `getstream` 6.1.0).
  - If a listing gets no 2xx, or a re-read cannot show an override, the run exits 4 with "not verified", and the case detail keeps the re-read's shape (key names only). Record that shape on the first live use.
- **Preflight** stops unless exactly one dashboard administrator exists and was created in the minute 24 September 2026 13:07 UTC. If it stops on the creation time, report it; do not bypass it.
- **Exit codes of `run`:** 0 clean; 2 stopped; 4 completed with a problem or an unverified item after it. The printed "after the run" lines say which.
- **`member.updated`:** I2a maps the event types with the filtered events view. `marker_event_types` names the event that carried the marker.
- **G2 and S10** still need the new setups the review describes (finding 6). The simulation now shows G2 as "not run", as the live runs did.
- **Budget:** the matrix now stops at 160 calls left (130 kept for the end of the run, plus 30), and preflight makes two more calls.

### Manager verification (App Manager 3, 26 September 2026)

App Manager 3 checked the relayed report against the pushed branch. The manager makes no call to Stream, so nothing here was exercised live; the first live use is in I2a.

- **Identity:**
  - branch `claude/youthful-pasteur-caokpc`, head `9e018c67858ccafa5f84dd75bcef51dcc3dfb49a`, tree `35ee86cecb5221f972e914c8c0f525c0888fa49b`; code head `be46319`;
  - it builds on the start `360ad9e` in seven commits: 29 files, +4,674 and −591;
  - every path is owned, and every file has mode 100644. No dependency file, `.npmrc`, `pyproject.toml` or the committed baseline changed, and `git diff --check` is clean;
  - the manager's two sections of this record, "Manager verification" and "Exact-head review of I1", are byte-identical to the start. The record carries 13 "(corrected in P06.1-C1)" markers.
- **Classification:** the trusted policy from `main` (`0f45e64`), run outside the tree with `python3 -I`, gave full scope (`behavior-or-empty`) for 29 paths, with one merge base.
- **Offline re-run,** in a scratch worktree at `9e018c6`, in clean processes without any `STREAM_*` variable. Installs got the proxy and CA variables by reference.
  - `pip install --require-hashes -r requirements-dev.lock`, then `pip check`: "No broken requirements found." `getstream` 6.1.0, Ruff 0.16.8, mypy 2.3.1.
  - `npm ci --ignore-scripts`: "found 0 vulnerabilities"; `stream-chat` 9.53.0.
  - Unit tests: `Ran 142 tests`, `OK`. Ruff check: "All checks passed!". Ruff format: "37 files already formatted". mypy: "no issues found in 36 source files". `node --check` on both `.cjs` files: exit 0.
  - `checks/fix_reversals.py`: "reversals: 51, not demonstrated: 0", exit 0, in about two minutes. The checkout was unchanged afterwards.
- **Secret scan** of the whole diff (320,008 bytes): no JWT-shaped string, email address, private-key block, AWS-style key, TLS-weakening setting or the application's API key.
- **Code read:** how a verdict gets Stream's answer (`_answer_of` and `_http_answer`, `proof_run.py` around line 130), the one-dashboard-user preflight (around line 600), and `cmd_run`'s stop handling and `finish()` (`cli.py` around line 140). Each matches the report. The exact-head review reads the whole change.
- **Integration:** merged into the manager branch as `e85bba0f054908a801b43e6f9d514b04f5fdbf78`, pushed alone at 03:44 UTC. The merge brings exactly C1's 29 files.
- **Hosted CI on `e85bba0`:** push run [36215753866](https://github.com/amthorn78/glow-dating-app/actions/runs/36215753866) and PR run [36215756463](https://github.com/amthorn78/glow-dating-app/actions/runs/36215756463) passed all six jobs, and the push run's gate says `Application checks passed`. The rendered suite passed 84 of 84 on the pinned Chromium in 3.9 minutes. No Foundation job runs the harness's own tests yet (I2b adds one); the offline re-run above covers them.
- **Disposition:**
  - nits 14 and 17 stand as recorded limits;
  - C1's own choices go to the exact-head review: a charge-signal stop still restores and re-reads; a failed undo stops the run; a removal that cannot be proven is "not verified", with exit 4;
  - "What P06.1-I2a must know" feeds I2a's prompt; the brief's "Sessions" points to it.

### Exact-head review of C1 (26 September 2026)

Nathan ran the review session at extra high, from revision 1 of the [review prompt](../../ephemeral/2026-09-26-p06-1-c1-review-prompt.md) (records commit `6178f2b`), and relayed its report. The session committed and pushed nothing, and made no Stream call.

- **Verdict: approve.** The corrected harness is a sound base for I2a's live runs. Findings 1 to 8 of the I1 review, and the 15 nits C1 claims, are confirmed fixed.
- **Three should-fix findings and seven nits remain.** None changes a recorded result. The reviewer recommends fixing the three before or alongside I2a.

#### The report, as relayed

The session's note before its report, verbatim:

> The adversarial pass is in. Before I use any of its findings I'll reproduce the two that matter most against the harness's own fakes: the T4-rest-unread hold with a failed control, and a FAIL observation being lost when a later step interrupts the case.
>
> All four reproductions confirm the candidate findings against the fakes, and the checkout is untouched. One last detail for the report: the path counts of the classification runs.

##### Identity, gates and verdict

**Prompt:** revision 1, from commit `6178f2b229784db90065f3f20cad77b482d3ff8d`.

**Head reviewed:** `git rev-parse HEAD` printed `e85bba0f054908a801b43e6f9d514b04f5fdbf78`. `HEAD^2` is `9e018c67858ccafa5f84dd75bcef51dcc3dfb49a`. `git merge-base --all origin/main HEAD` printed one line, `0f45e648099b415217938c25d7369164c0101def`. The ancestor check printed "records build on the head". `git diff --stat HEAD^1 HEAD` ended "29 files changed, 4674 insertions(+), 591 deletions(-)". The harness at HEAD is byte-identical to C1's code head `be46319`, and `HEAD^2..HEAD` differs only in three Markdown records.

**Environment:** none of `DATABASE_URL`, `HD_API_KEY`, `GEO_API_KEY` present. None of `STREAM_APP_ID`, `STREAM_API_KEY`, `STREAM_API_SECRET` present. Tools in `/root/.local/bin`: node v24.19.0, npm 11.9.0, npx 11.9.0, Python 3.12.14.

**Classifications** with the trusted `main` policy, extracted outside the tree and run with `python3 -I … --merge-base`:

| Run | Output |
|---|---|
| `main` → `e85bba0` | `{"full": true, "reason": "behavior-or-empty", …}`, 106 paths |
| `8b8b1bd` → `e85bba0` | `{"full": true, "reason": "behavior-or-empty", …}`, 41 paths; the non-Markdown, non-`proofs/stream-chat/` filter printed nothing |
| `e85bba0` → `6178f2b` | `{"full": false, "reason": "ordinary-docs-only", …}`, 6 Markdown paths |

**Verdict: approve.** The corrected harness is a sound base for P06.1-I2a's live runs. Findings 1 to 8 and the 15 nits C1 claims are fixed, each with a test that fails without it. I found no path to a HOLDS on a request Stream did not answer, and no path that leaves a temporary change in place with exit 0. Three should-fix findings remain, all inherited or at the edges of what the I1 review asked; none changes a recorded result, and each leaves a visible trace in the row. I recommend fixing them before or alongside I2a.

##### Findings, most severe first

1. **Should fix. A FAIL observed in a case is lost when a later step of that case is interrupted by anything other than a restore failure.** `proof_run.py:951-952` re-raises `GuardrailStop` without a row; `:967-985` build a fresh INCONCLUSIVE row for `ClientSessionEnded` and other exceptions; `_keep_case` at `:431` is wired only to `RunStopped`. Reproduced against the fakes: in S2 the client's thread reply succeeds with replies on, the restore succeeds, then the production request at `:1090` times out. The row reads "INCONCLUSIVE: a client session ended" with observed "not judged", and the bypass is gone. In S15, B reads the marker under production, then B's session ends during the control at `:1862`; the row is INCONCLUSIVE with an empty detail, against README line 151. In `_evaluate_case`, a 429 on the server replay at `:1125` raises before `_undo_client_success` at `:1153`, so the run stops with no row and no undo. Fix: keep the partial row on the run, as `_keep_case` does, and have every `except` branch in `run_matrix` consult it, appending a row before re-raising `GuardrailStop`.

2. **Should fix. T4-rest-unread can record HOLDS (accepted, not applied) with A's own control failed.** `proof_run.py:1405-1426`: `total()` returns `None` for a refused request or a 2xx without `total_unread_count`; `None != 1` and `None == None` then select the HOLDS_IGNORED branch, and `controls_ok` is consulted only in the refusal branch at `:1420`. Reproduced: A's own request refused, B's answered 1, the claim answered 2xx without the field; verdict "HOLDS (accepted, not applied): claim ignored", control "A's own total None; B's own total 1". Fix: require `controls_ok` and three non-`None` totals before any HOLDS_IGNORED; otherwise INCONCLUSIVE. README line 150 should say the success case needs the controls too.

3. **Should fix. RT2 and RT3 record HOLDS on any refusal, including 400 input errors, 404 and 5xx.** `proof_run.py:2094-2098`, documented at README line 147 as "any status". Reproduced: A's typing event answered 400 code 4 gives "HOLDS: refused (input); nothing delivered", and a 503 gives "HOLDS: refused (other)". A malformed request or a Stream outage says nothing about what a well-formed event delivers to B, and the matrix quality rule counts only attributable refusals. This is I1's rule, kept by C1 with the no-response exclusion added, so it is not a regression. Fix: HOLDS only for `auth`, `permission` and `feature` outcomes; `input`, `not-found` and `other` become INCONCLUSIVE "refusal not attributable"; update README line 147.

4. **Nit. After a charge-signal stop, restores are retried three times and the README undercounts the calls.** `finish()` at `proof_run.py:2366-2376` retries a "stopping at once" `GuardrailStop`, including a 402 or billing wording, after 10 s and 20 s. An AB override restore is PATCH, re-read and B's members probe per attempt, so up to 9 calls plus the 2 configuration reads, while README line 166 says "at most two or three calls per journalled change". None of these calls can incur a charge and the ledger still caps them, so the choice is safe. Suggest retrying only on 429 and Stream code 9, and correcting the README.

5. **Nit. A feature-gated case keeps HOLDS when its production-phase request has no recorded answer.** `proof_run.py:1105-1109` and `:1695` react only to a production success. README lines 188 to 191 say the request "must also fail" under production; a local throw or budget refusal there is neither. Suggest INCONCLUSIVE when the production answer is `no-response`.

6. **Nit. The "last HTTP request" rule is unchecked.** `proof_run.py:143-150` and `runner.cjs:304`. I confirmed in stream-chat 9.53.0 that every SDK method the matrix uses sends exactly one request with the runner's options, and that the latent extras such as the code-40 token retry, the delivered-events report and `/hi` are inactive. An SDK bump could add a trailing request. Suggest treating `len(reply.requests) != 1` as no-response; `setGuestUser` already goes through `_guest_post`.

7. **Nit. E5 records FAIL when A's stored user cannot be read.** `proof_run.py:2036`: `_server_user` returns `{}` for an empty listing and `{}.get("role") != "user"` is true. Conservative direction, but wrong. Suggest INCONCLUSIVE on an empty read.

8. **Nit. A second Ctrl-C inside `finish()` loses the results file.** `cli.py:183-198`: `problems` is unbound and `run-<prefix>.json` is never written; only the progress file survives. Documented at `proof_run.py:2359`. Suggest writing `run.results()` before the restores as well.

9. **Nit. A restore whose PATCH succeeded can be reported "not restored".** If the B-session probe at `proof_run.py:521` hits the budget guardrail, `finish()` breaks at `:2374` and records "temporary change not restored" though the override was removed and only unverified. Exit is non-zero either way.

10. **Nit. The key-pattern redaction misses `firebase_server_key`, `sqs_key` and `sns_key`.** `redaction.py:29-30`. No current output path writes the raw app object, since `baseline` now writes only `APP_SETTING_KEYS`, so this is defence in depth.

##### Confirmations, areas without findings, checks and limits

**Findings 1 to 8 of the I1 review, and each nit C1 claims fixed: confirmed.**

- Finding 1: `_answer_of`, `_http_answer` and `_ws_answer` at `proof_run.py:130-170` take status and code from the recorded response only; `Reply.status` and `Reply.code` are used by no verdict. G1 FAILs whenever `_guest_created` is set at `:1520`; G3 is INCONCLUSIVE unless the anonymous connect succeeded at `:1594`; RT2 and RT3 are INCONCLUSIVE on no-response at `:2086`; `error-info.cjs:42` reports `ws-api` only when the SDK's JSON carries `isWSFailure === false`, which the SDK sets only for Stream's own error frame at `index.node.js:11674`. Tests in `test_answers.py` and `ErrorInfoTest`; reversals fail on the verdict labels.
- Finding 2: journal entry before each enabling request at `:1081`, `:1486`, `:1655`, `:1919`; `_temporary` at `:386` restores on every exit and keeps a `GuardrailStop` in flight; `RunStopped` re-raised at `:953`; `finish()` at `:2356` restores, cleans up and verifies after any stop, error, timeout or Ctrl-C; `cmd_run` returns 0 only with no stop and no problem, and unrestored or unverified changes are problems. `test_temporary_changes.py` and `test_cli.py`.
- Finding 3: `:603-612` stop unless exactly one dashboard administrator exists and its `created_at` falls in `2026-09-24T13:07` UTC; no identifier is recorded; `_utc_minute` handles nanoseconds, digit strings and ISO with nine fractional digits and returns `None` otherwise, which stops the run. `test_preflight.py`.
- Finding 4: `LOCAL_EVENT_TYPES` at `matrix.py:49` covers all nine local events stream-chat 9.53.0 declares, plus `health.check`, which the runner already drops; `_events_split` at `:837` and `marker_event_types` at `:1792`. `test_events.py`, including the test that reads the installed SDK's `EVENT_MAP`. The records now say the realtime path is unproven.
- Finding 5: reader thread and queue at `client_bridge.py:142-146`, id check at `:202`, timeout, EOF, non-JSON and mismatch end the session at `:156`, later sends raise without being sent, `run_matrix` records INCONCLUSIVE at `:967`. `test_client_session.py` with fake runners, including two replies in one write.
- Finding 6, C1's part: `fakes.py:297-306` refuses the control guest's connect; `test_run_simulation` shows G2 "not run".
- Finding 7: `matrix.py:369-384`; `LeakTermsTest`, including a channel object without text counted as a leak.
- Finding 8: every listed claim is corrected in place and marked; the twelve exact markers plus the Ctrl-C variant match the manager's count of 13; the G2 and G3 channels rows changed only their action text; no observed value or verdict changed; the manager's sections are byte-identical to `93781c8`.
- Nits 1 to 13, 15 and 16: each at the location C1 lists, each with the named test, each reversal failing on the expected assertion or error. Nit 12's measured worst case is 115 calls for a failing guest restore and 112 for a failing override restore, both under the 130 reserve, and my own count of the theoretical worst case is 118.
- Nits 14 and 17, left: the reasons are sound. There is no listing of soft-deleted channels, and cleanup hard-deletes every recorded channel by ID with the task required to complete. The `deleted-user-…` user is deleted only when created after the run started, and preflight refuses any pre-existing one.

**Areas reviewed with no findings.** The verdict functions in `matrix.py:204-259`; every procedure's control uses Stream's recorded answer; the override re-read rule fails closed, since a key not shown while set is either checked by B's members query being refused again or recorded as not verified with exit 4; restore and cleanup touch only the run's own users, channels, polls and groups, with preflight's poll and group listing excluded; the three new server calls match `getstream` 6.1.0: `POST /api/v2/polls/query` with `filter` and `limit`, `GET /api/v2/usergroups` with `limit`, `POST /api/v2/chat/channels` with `filter_conditions` and `limit`, auth carried on raw requests by the SDK's client defaults; a non-2xx listing is "not verified" and exits 4; the response model has `config` with `grants` but no `config_overrides`, which the harness already tolerates; credentials: the allowlist, the runner's refusal, redaction and leak checks stand, and the new outputs hold counts, key names and proof IDs only; the tests drive the harness's logic against the fakes rather than the fakes' behaviour; scope: only `proofs/stream-chat/**` and the evidence record changed, no dependency file, `pyproject.toml`, `.npmrc` or baseline, every file mode 100644, no symlink.

**Checks run.**

| Check | Result |
|---|---|
| `git diff --check HEAD^1 HEAD` | No output, exit 0 |
| The three classifications | As tabled above |
| `python3.12 -m venv .venv`; `pip install --require-hashes -r requirements-dev.lock`; `pip check`; `npm ci --ignore-scripts` with proxy and CA variables by reference, all in `env -i` | Installed; "No broken requirements found."; getstream 6.1.0, ruff 0.16.8, mypy 2.3.1; "added 51 packages, and audited 52 packages", "found 0 vulnerabilities"; stream-chat 9.53.0, ws 8.21.3, https-proxy-agent 5.0.1 |
| `env -i PATH="$PATH" HOME="$HOME" LANG=C.UTF-8 .venv/bin/python -m unittest discover -s tests -t . -v` | `Ran 142 tests`, `OK` |
| `.venv/bin/ruff check .` / `.venv/bin/ruff format --check .` | "All checks passed!" / "37 files already formatted" |
| `.venv/bin/mypy` | "Success: no issues found in 36 source files" |
| `node --check client/runner.cjs`; `node --check client/error-info.cjs` | Exit 0; exit 0 |
| `.venv/bin/python checks/fix_reversals.py <scratchpad dir>` | "reversals: 51, not demonstrated: 0", exit 0; the Ctrl-C reversal aborts the test process as C1 said; `git status` clean afterwards |
| A scratch variant capturing each reversal's failure | All 51 fail on the expected assertion or error type |
| Secret scan of `git diff HEAD^1 HEAD`, 320,008 bytes | JWT-shaped strings 0, email addresses 0, private-key blocks 0, AWS-style keys 0, TLS-weakening settings 0, environment dumps 0; the only "secret" assignments are two synthetic test constants |
| Reproductions of findings 1 to 3 and nit 7 against the fakes | As described in the findings |
| Repository state | `git status --short` empty; only ignored `.venv`, `node_modules` and caches exist; no `.work/` |

**Limits.** No live behaviour was exercised, so Stream's real response shape for the channel re-read, and the poll and user-group listings, remain unseen. Hosted CI was not read; the manager reads it. Two read-only sub-agents helped: one verified SDK request shapes in the installed sources and one made an adversarial pass; I re-verified every item I took from them in the code or by reproduction, and neither made a Stream call. Nothing was committed, pushed or changed on GitHub or in Notion.

#### Manager verification of the review (App Manager 3, 26 September 2026)

The session committed nothing, so there is no branch to check. The manager checked the report's claims against the reviewed head.

- **Classification.** The manager re-ran all three with the trusted `main` policy and got the same results: 106 paths, full scope; 41 paths, full scope; 6 Markdown paths, `ordinary-docs-only`.
- **Findings, at `e85bba0`:**
  - **Finding 1:** `run_matrix` re-raises `GuardrailStop` with no row, and builds a fresh INCONCLUSIVE row for `ClientSessionEnded` and any other exception (`proof_run.py:951-985`). Only `RunStopped` carries the case's partial row (`_keep_case`, `:431`).
  - **Finding 2:** in T4-rest-unread, a refused or incomplete control makes A's total `None`; `None != b_total` and `claim_total == None` then give HOLDS_IGNORED without `controls_ok` being consulted (`:1405-1426`).
  - **Finding 3:** RT2 and RT3 end in HOLDS for any refusal outcome, `input`, `not-found` and `other` included (`:2093-2098`).
  - **Nit 10:** the sensitive-key patterns hold no `server_key`, `sqs_key` or `sns_key` part (`redaction.py:29-30`).
- **Not re-run by the manager:** the session's installs, tests, reversal runs and reproductions. They match what the manager re-ran for C1's verification.

#### Disposition

- **C1's code head `e85bba0` is approved.**
- **The three should-fix findings and the seven nits go to a second offline correction pass, P06.1-C2, before I2a's live runs.** Findings 2 and 3 let a case record HOLDS without an attributable refusal and a successful control, which the brief's matrix quality rule forbids, and finding 1 can turn an observed FAIL into INCONCLUSIVE. Live budget is spent only on a harness whose verdicts are sound.
- **C2's exact-head review follows,** offline. I2a comes after it.

## P06.1-C2 corrections

The second correction pass on the harness, for the C1 review's findings 1 to 3 and nits 4 to 10. It made no Stream call and ran none of the harness's live commands. The first live use of these fixes, and of C1's, is in P06.1-I2a.

- **Prompt:** revision 1, from commit `5fc3bea2b62e50ad4f4357d55aa47b2d3a6cb67e`.
- **Branch:** `claude/lucid-einstein-79bqmd`. **Start:** `5fc3bea2b62e50ad4f4357d55aa47b2d3a6cb67e`.
- **Code head:** `f1c670b0ad7e650043e8bc35de3da4fcc2201d06`. It carries every code change and the records corrected below, and every check below ran on it. The commit that adds this section changes only this record.
- **Date:** 26 September 2026.

### Environment and start gate

| Check | Result |
|---|---|
| `DATABASE_URL`, `HD_API_KEY`, `GEO_API_KEY` | None present (the check printed nothing) |
| `STREAM_APP_ID`, `STREAM_API_KEY`, `STREAM_API_SECRET` | None present (the check printed nothing) |
| `command -v node npm npx python3.12` | `/root/.local/bin/node`, `/root/.local/bin/npm`, `/root/.local/bin/npx`, `/root/.local/bin/python3.12` |
| Versions | node v24.19.0; npm 11.9.0; Python 3.12.14 |
| Start gate | `git fetch origin claude/stoic-carson-66gdig`; `git merge --ff-only 5fc3bea…` fast-forwarded; `git rev-parse HEAD` printed `5fc3bea2b62e50ad4f4357d55aa47b2d3a6cb67e`; `git diff --stat e85bba0… HEAD -- proofs/stream-chat/` printed nothing |

The environment was never dumped. There were no connections to Stream, a database, HDE or Railway, and no `playwright install`, `eas` or `migrate`. Installs got the proxy and CA variables by reference.

### Findings 1 to 3 and nits 4 to 10

Paths are under `proofs/stream-chat/`; line numbers are at the code head. Each test named fails with its fix reverted and passes with it (see "Checks", item 5). The suggested fix was used for every item unless the row says otherwise.

| Item | Status | Where | Tests |
|---|---|---|---|
| 1. An observed FAIL lost when a later step is interrupted | Fixed. Each case keeps what it has observed so far (`_observe`, `glow_stream_proof/proof_run.py:472`), at every step after which a later step can be interrupted: the client's request before its control (`:1222`), the feature-on phase, bad-token REST and WebSocket, T4-rest-xd, G1, the guest and anonymous probes, S10 (with polls on, and before the production vote), S15 under production, S14 (the connection, then the stored state), E5 (the connection, then the stored role), RT1, and RT2/RT3's first window. Every way a case ends records its row (`run_matrix`, `:1046`; `_interrupted_row`, `:498`): a FAIL stays a FAIL, anything else becomes INCONCLUSIVE, "interrupted before the case finished: …". A client success whose undo is owed is undone after the control and the row records each undo (`:1278`); if the control is interrupted, `_undo_after_interruption` (`:1296`) follows the README's rule on what may still run after each kind of stop (see "Decisions") | `tests/test_interruptions.py`: `ReviewScenariosTest` (the review's three scenarios: S2, S15, and S3a's server replay under a rate limit, under a harness error and under Ctrl-C), `EveryWayACaseEndsTest`, `ProceduresKeepWhatTheyObservedTest` (one test per place that keeps an observation) |
| 2. T4-rest-unread HOLDS with A's control failed | Fixed. Neither kind of HOLDS without both controls; "HOLDS (accepted, not applied)" also needs all three totals, each from a 2xx answer to the one request (`:1620`, `:1638`). A FAIL on the claim's total equal to B's needs them too. README "Verdict rules", T4-rest-unread | `tests/test_procedures.py` `UnreadControlsTest` (including the review's reproduction) |
| 3. RT2 and RT3 HOLD on any refusal | Fixed. A refusal HOLDS only for `auth`, `permission` or `feature`; `input`, `not-found` and `other` are INCONCLUSIVE, "refusal not attributable (…)" (`:2476`). Named events count only after an accepted request (`:2472`), so events after a non-attributable refusal are INCONCLUSIVE too. README "Verdict rules", RT2 and RT3 | `tests/test_answers.py` `PayloadRefusalAttributionTest` |
| Nit 4. Charge-signal restores retried; README undercount | Fixed. A `GuardrailStop` says whether it was a rate limit (`glow_stream_proof/usage.py:42`, `is_rate_limit` `:147`: HTTP 429 or Stream code 9, unless 402 or code 99), set at all four raise sites (`server_api.py:109`, `:151`; `client_bridge.py:259`, `:266`). `finish()` retries a restore only after a rate limit or a failure that is not a stop signal (`proof_run.py:2779`). README's count corrected: at most six calls per journalled change when its restores meet a charge signal or the budget, twelve otherwise, plus two configuration reads | `tests/test_temporary_changes.py` `RateLimitRetryTest`; `tests/test_server_api.py` `RateLimitFlagTest`; `tests/test_client_session.py` `ClientRateLimitFlagTest` |
| Nit 5. Production phase with no answer keeps HOLDS | Fixed. A feature-gated case (S2, S5, S6, S7, S12) and S10 are INCONCLUSIVE when the production-phase request has no recorded answer, unless already FAIL or INCONCLUSIVE (`:1194`, `:1961`) | `tests/test_answers.py` `ProductionPhaseAnswerTest` |
| Nit 6. "Last HTTP request" unchecked | Fixed. `_http_answer` gives no answer for a reply with more than one recorded request (`:157`); G1's `POST /guest` must be the one request the command recorded (`_guest_post`, `:1775`). Every caller of `_http_answer` was checked: each judges an SDK call that sends exactly one request (watch, query, queryMembers, markRead, getUnreadCount, castPollVote and the matrix's single calls). G1 still FAILs whenever a guest was created | `tests/test_answers.py` `OneRequestTest` |
| Nit 7. E5 FAIL on an unreadable stored user | Fixed, and extended to S14, which had the same defect in the other direction (an unreadable user counted as unchanged). `_server_user` returns `None` unless the listing holds that ID (`:2227`), which held for a 2xx listing only: a listing Stream did not answer with 2xx made `ServerApi.require` raise, so the row read "harness error" and the run went on, until P06.1-C3; the fakes' `require` does not raise, which hid it (corrected in P06.1-C3); E5 and S14 are then INCONCLUSIVE, "A's stored user could not be read", unless the connection's user object already showed the change (`:2408`, `:2324`) | `tests/test_procedures.py` `StoredUserUnreadableTest` |
| Nit 8. A second Ctrl-C inside `finish()` loses the results file | Fixed. `cmd_run` writes the results before the end of the run (`glow_stream_proof/cli.py:187`, marked `end_of_run: not finished`), and a second Ctrl-C inside `finish()` is caught (`:206`): the client processes are closed, the results are written with the problem "the end of the run was interrupted", exit 2. `finish()` keeps its problems on the run as it finds them (`proof_run.py:2766`) | `tests/test_cli.py` `CommandTest.test_second_ctrl_c_inside_finish_keeps_the_results_file`, `test_results_are_written_before_the_end_of_the_run`, `test_ctrl_c_during_the_early_write_still_restores` |
| Nit 9. An accepted, unverified removal reported "not restored" | Fixed. A removal of AB's override whose PATCH was accepted, with no key still reading as overridden, but whose B probe was stopped by a guardrail, is recorded as not verified and leaves the journal (`:605`, `:618`; `_restore` `:423`, `_restored_unverified` `:450`); the stop still propagates. If a key still reads as overridden, the change stays journalled | `tests/test_temporary_changes.py` `UnverifiedRemovalTest`; `tests/test_interruptions.py` `ReviewOfC2Test.test_a_key_still_overridden_keeps_the_change_journalled` |
| Nit 10. Key-pattern redaction misses credential keys | Fixed. Any key ending in `_key` is redacted (`glow_stream_proof/redaction.py:35`). A walk of `getstream` 6.1.0's `GetApplicationResponse` and every model it contains (57 models, 312 field names) found seven credential names the patterns missed: `firebase_server_key`, `server_key`, `sqs_key`, `sns_key`, `s3_api_key`, the Datadog `api_key` and the RTMP `stream_key`. All are now covered. The Datadog `api_key` means `api_key` is redacted by key everywhere, including the client-safe Stream API key in recorded request parameters; plain-text redaction is unchanged | `tests/test_redaction.py` `test_credential_keys_of_the_app_settings_model_are_redacted`; `test_the_harness_marker_fields_are_never_redacted` |

C1's own tests changed in three places, each to the new rule or to check more: `test_sensitive_keys_are_matched_by_pattern` no longer asserts that `api_key` stays unredacted (nit 10); `GuardedUnsetTest` now expects S15's row after the guardrail stop, where it expected none (finding 1); `test_rt2_local_throw_is_inconclusive` and `test_rt3_null_return_without_a_request_is_inconclusive` also check the reason, because finding 3's rule would otherwise also make them INCONCLUSIVE and hide C1's no-answer rule.

### The independent review of these corrections

A read-only sub-agent reviewed the uncommitted diff adversarially, reproduced each point against the fakes, and made no Stream call. I verified each point and fixed all four:

1. **E5 lost a stored-role FAIL.** E5 kept only its connection's result before reading the stored user, so a restore of A's role that was interrupted turned "admin reached stored state" into INCONCLUSIVE; a restore that raised an exception let the run go on with A holding the role. E5 now keeps the FAIL before its restore, and a restore that raises stops the run after E5's row (`proof_run.py:2398`). Tests: `ReviewOfC2Test.test_e5_…` (two).
2. **A failing progress write could replace a guardrail stop.** In the new stop branches, a `progress()` that raised (a full disk, a leak refusal) replaced the `GuardrailStop`, so `cmd_run` saw a harness error and ran cleanup after a charge signal. A regression from C1, found before commit. Progress is now written quietly while a stop is in flight (`_progress_quietly`, `:1068`). Tests: `ReviewOfC2Test.test_a_failing_progress_write_never_replaces_a_guardrail_stop`, `test_ctrl_c_is_kept_when_the_progress_write_fails`.
3. **Nit 9 could drop a change still in place,** with two keys in one override (not reachable with today's single-key overrides). A key that still reads as overridden now wins, and the change stays journalled (`:618`). Test: `ReviewOfC2Test.test_a_key_still_overridden_keeps_the_change_journalled`.
4. **The early results write was not fully protected.** It now sits wholly inside its `try`, which also catches a Ctrl-C (`cli.py:197`), so the restores still run; every `.work` file except the usage ledger is written through a temporary file and renamed (`glow_stream_proof/workdir.py:27`), and the ledger was written directly until P06.1-C3 (corrected in P06.1-C3); `finish()` keeps its problems as it finds them. Tests: `CommandTest.test_ctrl_c_during_the_early_write_still_restores`, `AtomicWriteTest`, `ReviewOfC2Test.test_finish_keeps_the_problems_found_before_a_second_ctrl_c`.

It also raised points left as they are, listed under "Decisions" and "Limits".

### Records corrected

In this record, each edited in place and marked "(corrected in P06.1-C2)". No recorded result changed, and the four sections the prompt protects are unchanged byte for byte.

- **I1's "Deviations", "A run's results were lost":** "since P06.1-C1 Ctrl-C is handled too" was not true at C1's head for a second Ctrl-C inside the end of the run (nit 8).
- **C1's nit 8 row:** "credential keys are matched by pattern" missed seven credential key names (nit 10).
- **C1's nit 16 row:** "T4-rest-unread HOLDS without its controls — Fixed" held for a refusal only; an accepted claim could still give HOLDS (accepted, not applied) without its controls (finding 2), and an unreadable stored user made E5 a FAIL (nit 7).

In `proofs/stream-chat/README.md`, each rule as the code now applies it, with the changed ones marked: the verdict rules (one request; E5 and S14 unreadable users; interrupted cases; the undo of a client success; feature-gated cases; G1; RT2 and RT3; T4-rest-unread), the end-of-run sequence (restore retries, "not verified", the early and atomic results writes, the second Ctrl-C), the stop and restore rules, and the call counts after a charge signal ("at most two or three calls per journalled change", corrected). The offline checks now list `node --check client/error-info.cjs`.

### Checks

Run from `proofs/stream-chat/` unless noted, at code head `f1c670b`, in clean processes (`env -i`), with no `STREAM_*` variable present.

| # | Check | Result |
|---|---|---|
| 1 | `git diff --check 5fc3bea… HEAD` (repository root) | No output, exit 0 |
| 1 | `git diff --name-only 5fc3bea… HEAD` | 18 paths: this record and 17 under `proofs/stream-chat/` (one new file, `tests/test_interruptions.py`). All owned; no dependency file, `.npmrc`, `pyproject.toml` or baseline change; every file mode 100644, no symlink. 2,377 insertions, 198 deletions |
| 2 | The trusted policy from `origin/main` (`0f45e64`), extracted to a temporary directory outside the tree, run with system Python 3.11.15: `python3 -I change_scope.py --base 5fc3bea… --head f1c670b… --merge-base` | Exit 0; `{"full": true, "reason": "behavior-or-empty", …}`, 18 paths. One merge base, `5fc3bea…`. Full scope, as expected |
| 3 | From deleted `.venv` and `node_modules`: `python3.12 -m venv .venv`; `.venv/bin/python -m pip install --require-hashes -r requirements-dev.lock`; `pip check`; `npm ci --ignore-scripts` (proxy and CA variables by reference) | Python 3.12.14; "No broken requirements found."; `getstream` 6.1.0, Ruff 0.16.8, mypy 2.3.1; "added 51 packages, and audited 52 packages", "found 0 vulnerabilities"; `stream-chat` 9.53.0, `ws` 8.21.3, `https-proxy-agent` 5.0.1 |
| 4 | `env -i PATH="$PATH" HOME="$HOME" LANG=C.UTF-8 .venv/bin/python -m unittest discover -s tests -t . -v` | At the start (`5fc3bea`): `Ran 142 tests`, `OK`. At the head: `Ran 202 tests`, `OK` |
| 4 | `.venv/bin/ruff check .` / `.venv/bin/ruff format --check .` | "All checks passed!" / "38 files already formatted" |
| 4 | `.venv/bin/mypy` | "Success: no issues found in 37 source files" |
| 4 | `node --check client/runner.cjs`; `node --check client/error-info.cjs` | Exit 0; exit 0 |
| 5 | `.venv/bin/python checks/fix_reversals.py <scratch dir>` | At the start: "reversals: 51, not demonstrated: 0", exit 0. At the head: "reversals: 99, not demonstrated: 0", exit 0: C1's 51 and 48 for C2, covering findings 1 to 3, nits 4 to 10 and the four review points. Four reversals ended without a test report. Three, C1's one Ctrl-C reversal and C2's two for nit 8 and the early write, fail by the Ctrl-C escaping and aborting the test process, which the script counts as failing. The fourth, C1's "F2 end of run", failed only because its 8-space pattern matched inside a 12-space line and the edited `cli.py` did not compile, so it was not demonstrated: 98 of the 99 were (corrected in P06.1-C3). The checkout was unchanged afterwards |
| 6 | Secret scan of `git diff 5fc3bea… f1c670b` (177,517 bytes) | JWT-shaped strings 0; email addresses 0; private-key blocks 0; AWS-style keys 0; the application's API key 0; TLS-weakening settings 0; environment dumps 0; no secret or token assignment in added lines; every long token-like string is a test name |

Not run: any live command, and the repository's Foundation CI (not triggered by this session, and it does not run this harness's tests).

### Decisions, deviations and limits

- **Decisions to confirm.**
  - **The undo of a client success after an interrupted control** (finding 1's third scenario). Chosen from the README's rule on what may still run after each kind of stop: after a guardrail stop it is not made (a charge or limit signal stops the run at once and deletes none of its data; the budget has no calls left), and after Ctrl-C it is not made (at C2's head "deletes none of its data" held only for a signal that was the run's own stop: one first met by the end of the run, or behind another stop kept as the run's stop, did not stop the cleanup, the C2 review's finding 2 (corrected in P06.1-C3)); after an ended client session, a failed restore or a harness error it is made. The row says which and why. The change is always to the run's own synthetic data, which cleanup deletes (after a charge signal, `cleanup --apply`). An undo that itself hits a guardrail becomes the run's stop, with the interruption kept in the stops.
  - **Nit 7 extended to S14,** the same defect in the same helper.
  - **T4-rest-unread's FAIL needs its evidence too:** a claim total equal to B's is a FAIL only with both controls and all three totals; otherwise INCONCLUSIVE. No HOLDS rule became weaker; this FAIL rule and E5's (nit 7) now give INCONCLUSIVE, not a pass, on missing evidence.
  - **RT2/RT3 HOLD on a `feature` refusal** (400 code 18 or 19), as the prompt directs; I1's recorded RT2 was one. The review noted that this sits beside the matrix quality rule's "authentication or permission error" and the matrix-wide REFUSED_FEATURE label, and that the refusal branch has no control beyond B's listening probe. Left for the manager.
  - **`is_rate_limit` ignores the response's wording,** so a 429 that mentions billing is retried; excluding wording would also exclude "rate limit exceeded".
- **Deviations.** Beyond the ten items: the four review points above; atomic `.work` writes; `node --check client/error-info.cjs` added to the README's offline checks. New file: `tests/test_interruptions.py`.
- **Limits.**
  - Nothing here was exercised live; the tests prove the harness's logic against fakes.
  - Nit 6 makes any reply with more than one recorded request INCONCLUSIVE, so a real 2xx bypass that also sent an extra request would read INCONCLUSIVE, not FAIL, and owes no undo; the observed text shows the request count.
  - After an interruption, S14's restore of A's name and E5's restore of A's role (when a guardrail stopped it) are left to cleanup, which deletes A.
  - Existing behaviour, unchanged: T4-ws's HOLDS (accepted, not applied) does not consult its control; after a charge signal, `_temporary`'s restore (by design) and S15's unset of A's member field still send requests.
  - Redaction by key name hides a value from the leak checks too; the harness's marker fields do not match any credential pattern, and a test keeps it so. Credentials inside URL values are not redacted by key.
- **No dependency change,** and nothing outside the owned paths.

### What P06.1-I2a must know

In addition to C1's list above:

- **Rules that changed** (README "Verdict rules" states each):
  - an interrupted case records its row: a FAIL stays a FAIL, anything else is INCONCLUSIVE with the interruption named in `detail.interrupted`;
  - T4-rest-unread HOLDS only with both controls and all three totals;
  - RT2 and RT3 HOLD on a refusal only for `auth`, `permission` or `feature`;
  - a feature-gated case, and S10, is INCONCLUSIVE when its production-phase request has no answer;
  - a command with more than one recorded request has no answer; G1's `POST /guest` must be the only request;
  - E5 and S14 are INCONCLUSIVE when A's stored user cannot be read;
  - a failed restore of A's role in E5 stops the run.
- **Stop and restore rules that changed:** among stop signals, only a rate limit (HTTP 429 or Stream code 9) is retried at the end of the run; an accepted removal that cannot be verified is "not verified" (exit 4 if the run completed), not "not restored"; the client-success undo rule above.
- **Outputs that changed:** `run-<prefix>.json` is written before the end of the run (`end_of_run: not finished`) and again after it; a second Ctrl-C inside the end of the run exits 2 with "the end of the run was interrupted" (then run `configure` as a dry run and `verify-clean`); `.work` files are written through a `.partial` file, except the usage ledger until P06.1-C3 (corrected in P06.1-C3); case rows may carry `interrupted` and `client_success_undo` in their detail; recorded `api_key` parameters read `<redacted-secret>`.
- **Not exercised live:** every fix above, including the `rate_limited` flag on Stream's real 429 and code-9 answers, and the call counts after a charge signal.

### Manager verification of C2 (App Manager 3, 26 September 2026)

App Manager 3 checked the relayed report against the pushed branch. The manager makes no call to Stream, so nothing here was exercised live; the first live use is in I2a.

- **Identity:**
  - branch `claude/lucid-einstein-79bqmd`, head `ba36311ae86e7c9ded4f6d6c5ae66acdfb517150`, tree `55995bc4da7ed3ae0688fd7c0a21a25f5908beb4`; code head `f1c670b`;
  - it builds on the start `5fc3bea` in two commits: 18 files, +2,490 and −198. The second commit changes only this record;
  - every path is owned, and every file has mode 100644. No dependency file, `.npmrc`, `pyproject.toml` or the committed baseline changed, and `git diff --check` is clean;
  - the four sections the C2 prompt protects are byte-identical to the start. The record carries three in-place "(corrected in P06.1-C2)" markers.
- **Classification:** the trusted policy from `main` (`0f45e64`), run outside the tree with `python3 -I`, gave full scope (`behavior-or-empty`) for 18 paths, with one merge base.
- **Offline re-run,** in a scratch worktree at `ba36311`, in clean processes without any `STREAM_*` variable. Installs got the proxy and CA variables by reference.
  - `pip install --require-hashes -r requirements-dev.lock`, then `pip check`: "No broken requirements found." `getstream` 6.1.0, Ruff 0.16.8, mypy 2.3.1.
  - `npm ci --ignore-scripts`: "found 0 vulnerabilities"; `stream-chat` 9.53.0.
  - Unit tests: `Ran 202 tests`, `OK`. Ruff check: "All checks passed!". Ruff format: "38 files already formatted". mypy: "Success: no issues found in 37 source files". `node --check` on both `.cjs` files: exit 0.
  - `checks/fix_reversals.py`: "reversals: 99, not demonstrated: 0", exit 0, in 4 minutes 19 seconds. The checkout was unchanged afterwards.
- **Secret scan** of the whole diff (197,542 bytes): no JWT-shaped string, email address, private-key block, AWS-style key, TLS-weakening setting, environment dump, secret assignment or the application's API key.
- **Code read,** at `ba36311`. Each matches the report:
  - the one-request rule in `_http_answer` (`proof_run.py` around line 148);
  - `_observe`, `_interrupted_row` and `run_matrix`'s branches (around lines 472 to 522 and 1024 to 1066);
  - the feature-gated production phase (around line 1190) and `_undo_after_interruption` (around line 1286);
  - T4-rest-unread's controls and totals (around line 1620), and RT2 and RT3's refusal rule (around line 2470);
  - `finish()`'s retry rule with `is_rate_limit` (around line 2766; `usage.py` around line 147), and the "not verified" removal (around lines 421 and 585 to 627);
  - E5's kept FAIL and its restore (around line 2388);
  - the early results write and the second Ctrl-C (`cli.py` around lines 183 to 215), and the `_key` suffix (`redaction.py` around line 35).
- **Integration:** merged into the manager branch as `63e922fb86f214b99627748cbb53387baa6dd748`, pushed alone at 12:30 UTC. The merge brings exactly C2's 18 files, and its tree is C2's head tree.
- **Hosted CI on `63e922f`:** push run [36242106508](https://github.com/amthorn78/glow-dating-app/actions/runs/36242106508) and PR run [36242109996](https://github.com/amthorn78/glow-dating-app/actions/runs/36242109996) passed all six jobs, and the push run's gate says `Application checks passed`. The rendered suite passed 84 of 84 on the pinned Chromium in 3.8 minutes. No Foundation job runs the harness's own tests yet (I2b adds one); the offline re-run above covers them.

#### The decisions C2 left to the manager

- **The undo of a client success after an interrupted control: C2's rule stands.** After a guardrail stop or Ctrl-C the undo is not made, and the row says so; after anything else it is made. It follows the README's rule on what may still run after each kind of stop, and Nathan's $0 budget (OD-12): nothing more is sent for the run's own data after a charge or limit signal, and cleanup deletes that data.
- **RT2 and RT3: a `feature` refusal gets "REFUSED (feature off; not a permission error)", not HOLDS.** The C2 prompt directed HOLDS, and C2 built it so. The manager changes that direction, for three reasons:
  - the brief's matrix quality rule, and the first paragraph of the README's own "Verdict rules", count a refusal only when it is an authentication or permission error;
  - the matrix gives every other feature refusal that verdict;
  - for RT2, only the configuration protects B. I1 showed that, with typing on, typing events carry any custom field the client adds, and no permission governs them (the I1 record's "Findings", item 2). The verdict keeps that visible for P06.2.

  I1's recorded RT2 result stays as recorded. The change goes into the next session that changes the harness, before any live run, with a test and a reversal. The direction was the manager's mistake (AM3-16).
- **Accepted as C2 chose:** nit 7 extended to S14; T4-rest-unread's FAIL needing both controls and all three totals, like its HOLDS; `is_rate_limit` ignoring the response's wording.

#### Disposition

- **C2 is verified and integrated at `63e922f`.** Its limits stand as recorded, and "What P06.1-I2a must know" feeds I2a's prompt, with C1's list.
- **C2's exact-head review is next,** offline. I2a comes after it.

### Exact-head review of C2 (26 September 2026)

Nathan ran the review session at extra high, from revision 1 of the [review prompt](../../ephemeral/2026-09-26-p06-1-c2-review-prompt.md) (records commit `6a439cf`), and relayed its report. The session committed and pushed nothing, and made no Stream call.

- **Verdict: approve.** The corrected harness is a sound base for I2a's live runs. The C1 review's findings 1 to 3 and nits 4 to 10, and C2's own four review points, are confirmed fixed. The reviewer agrees with both of the manager's decisions on C2.
- **Two should-fix findings and eight nits remain.** None creates a HOLDS without Stream's refusal, and none changes a recorded result. The reviewer recommends fixing both should-fix findings before any live run, in the session that makes the RT2 and RT3 change.

#### The report, as relayed

The session's notes before its report, verbatim:

> Reading C2's changes to the existing test files now; both reversal runs are still going in the background.
>
> Checked the `_key` redaction against both SDKs' response models: no chat response field the matrix reads ends in `_key`. Now checking whether any replay reuses a recorded `api_key` parameter.
>
> Both reversal runs are still going. Meanwhile I'm writing extra mutations of my own to find fixes whose tests would still pass if the fix were broken a different way.
>
> All 48 of C2's reversals fail on the expected assertion. Checking C1's 51 as well, especially the three whose tests C2 changed.
>
> Reversal 8 (C1's "end of run" reversal) now fails with a `SyntaxError`, not an assertion. Checking whether C2's `cli.py` change broke it.
>
> Reversal 8 is broken here—its 8-space pattern now falls inside C2's 12-space `try:` block, causing a SyntaxError instead of properly reverting the fix. I'll check whether a corrected reversal still gets caught.
>
> `rsync` is missing, so that chain stopped before any edit; the tests ran on the unmodified checkout. Confirming the checkout is untouched, then redoing it with `cp`.
>
> The tests still catch reversal 8 when it is done correctly, so only the script's pattern is stale. Both background runs have finished; reading their logs.
>
> The official script's summary looked clean (99 reversals, 0 undemonstrated) but reversal 8 actually failed silently with a SyntaxError. Of my 20 extra mutations, 6 slipped through revealing genuine test gaps and 2 hit redundant code; now I'm reviewing the rest of the proof_run.py diff to make sure I haven't missed any hunks.
>
> I've now read every hunk of the `proof_run.py` diff. Checking the README's claim that every `.work` file is written atomically.
>
> I found that the usage ledger (usage.py:78) skips the atomic write, making the README's "every `.work` file" claim slightly overstated. Next I'll check the records: protected sections, the three corrections, and confirm no results changed.
>
> The three in-place corrections are at lines 478, 921 and 929 and each carries the marker. Now comparing the four protected sections byte for byte against `5fc3bea`.
>
> The three markers plus one quoted mention match C2's record. Next, verifying nit 10's claim by walking `getstream` 6.1.0's app-settings models myself.
>
> Nit 10's walk reproduces exactly: 57 models, 312 field names, and the same seven names missed at C1, all covered now. Next, the secret scan over the whole diff.
>
> Scope checks pass: 50 files, all mode 100644, no symlinks/executables, no dependency or baseline changes, and the secret scan found nothing. Next I'll check how a nit 6 row displays when a command records two requests.
>
> I found that a 2xx response on the first of two recorded requests leaves no trace in the row—no request info, statuses, or undo. I'm now checking that the SDK calls behind `_http_answer` each send exactly one request in stream-chat 9.53.0.
>
> Each of those SDK methods sends one request. Next, checking whether any chat response model the matrix reads could carry a leak term under a `_key` field such as `config_key`.
>
> `config_key` appears only in moderation models, not in any chat response the matrix reads, so the `_key` suffix hides nothing today. Next, counting which reversals abort instead of failing normally.
>
> Four reversals cancel out to an empty "reverted:" result, but C2's account of "two Ctrl-C reversals from C1" doesn't match—C1 only logged one, so the fourth must be reversal 8's SyntaxError. I'll verify reversal 8 was a genuine demonstration at C1's head commit, `e85bba0`.
>
> Confirmed: at `e85bba0` reversal 8 failed on assertions; at this head it fails only through the `SyntaxError`. Now a concrete check that S15 still sends its unset after a charge signal.
>
> Confirmed: S15 sends its unset `PATCH` after B's 402. Now demonstrating the `finish()` path: a charge signal met during the end-of-run restore.
>
> Confirmed that when the end-of-run restore hits a 402, `finish()` still completes the full cleanup (15 requests, including both hard deletes). I also noticed in `_generic_case` that `if not on.ok` sets INCONCLUSIVE even when the feature-on phase already logged a FAIL, so I'll check if that's C1's code and try to reproduce it.
>
> I've confirmed the bug: A's reply succeeds while the enabling PATCH returns 500, yet the row logs INCONCLUSIVE "could not enable" while still showing "201 (succeeded)" — this is C1's unchanged code. Now I'll check the verdict helpers for other ways a FAIL could get downgraded.
>
> Confirmed the enable-failure path is the only way to rewrite an observed FAIL, since the other verdict override can't downgrade one. Now gathering exact line numbers for the report.
>
> Findings are settled. Final state check: the checkout must be unchanged, with only ignored paths created.
>
> Checks are done and the checkout is clean. Before writing the report I'll load Nathan's reporting skill, since it governs messages that report findings.

The report:

**Verdict: approve.** The corrected harness is a sound base for P06.1-I2a's live runs. Two should-fix findings and eight nits remain. None creates a HOLDS without Stream's refusal, and none changes a recorded result. I recommend fixing both should-fix findings in the session that makes the manager's RT2/RT3 change before any live run.

Correction to my interim note: 11 of my 20 extra mutations survived, not 8. Seven expose test gaps and four touch redundant or dead code.

##### Identity

- **Prompt:** revision 1, from commit `6a439cfbf7573f4dd0cc596b06e92d3813308616`.
- **Head reviewed:** `git rev-parse HEAD` printed `63e922fb86f214b99627748cbb53387baa6dd748`.
  - `HEAD^2` is `ba36311ae86e7c9ded4f6d6c5ae66acdfb517150`.
  - There is one merge base, `0f45e648099b415217938c25d7369164c0101def`.
  - The ancestor check printed "records build on the head".
  - `git diff --stat HEAD^1 HEAD`: 18 files, 2490 insertions, 198 deletions.
- **Environment:** none of `DATABASE_URL`, `HD_API_KEY`, `GEO_API_KEY` or the three `STREAM_*` variables is present. node v24.19.0, npm 11.9.0 and Python 3.12.14, all from `/root/.local/bin`.
- **Classifications:** the trusted `main` policy, extracted outside the tree and run with `python3 -I`; all three exited 0.

| Run | Output |
|---|---|
| `main` → head | `{"full": true, "reason": "behavior-or-empty"}`, 109 paths |
| `e85bba0` → head | `{"full": true, "reason": "behavior-or-empty"}`, 24 paths; the non-Markdown filter outside `proofs/stream-chat/` printed nothing |
| head → `6a439cf` | `{"full": false, "reason": "ordinary-docs-only"}`, 6 paths |

##### Findings, most severe first

Paths are under `proofs/stream-chat/`.

**1. Should fix. A feature-gated case's observed FAIL becomes INCONCLUSIVE when the enabling request was not 2xx.** `glow_stream_proof/proof_run.py:1187-1189`
- **Reproduced against the fakes:** in S2, the PATCH enabling replies got 500, and A's thread reply got 201.
  - The row reads "INCONCLUSIVE: could not enable {'replies': True} (channel AB, 500)".
  - Its observed text still says "feature on: 201 (succeeded); feature off (production): 403 / code 17".
  - A client action that must be refused succeeded, whatever the configuration was.
- This is C1's code, inside the block C2 rewrote. It is the only path I found that rewrites an observed FAIL.
- **Fix:** `if not on.ok and result.verdict != matrix.FAIL:`, with a test and a reversal.

**2. Should fix. A charge or rate-limit signal first met during the end of the run does not skip cleanup.** `proof_run.py:2774-2794` (`finish()`), and `:417-418` (`_temporary`)
- **Reproduced:** the run stopped on a failed restore, so `cleanup_needed` stays true. `finish()`'s retry then got HTTP 402.
  - The 402 is recorded as a problem, and then the full cleanup runs: 15 requests in the fake, including the channel and user hard deletes.
  - Live, cleanup breaks at its first delete if Stream keeps answering 402, so at least one request follows the signal. If the signal was specific to one endpoint, the whole cleanup runs.
  - Three rate-limited retries also end in a cleanup.
- **Variant:** `_temporary` keeps an in-flight budget or connection `GuardrailStop` as the run's stop, even when the restore met a charge signal. `cmd_run`'s "stopping at once" test then misses the signal.
- This contradicts README line 177, "After such a stop the run deletes none of its users or channels". It is not silent: the exit is 2 and the 402 is printed.
- **Fix:**
  - flag the run whenever a charge or limit signal is seen;
  - have `finish()` skip cleanup, with the problem "cleanup skipped: …";
  - have `cmd_run` consult the flag.

**3. Nit. C1's reversal "F2 end of run" no longer reverts its fix.** `checks/fix_reversals.py:164`
- Its 8-space pattern now matches inside C2's 12-space `try:` at `cli.py:205`. The edit produces `SyntaxError: expected 'except' or 'finally' block`, and the script counts that as demonstrated.
- At `e85bba0` it failed on assertions. With a correct 12-space reversal, its three tests still fail at this head (`0 != 4`, `0 != 4`, and the journal list). So the tests are sound; only the demonstration is broken.
- The real count is 98 of 99 demonstrated. C2's record misreads it as "C1's two Ctrl-C ones"; C1 had one Ctrl-C reversal.
- **Fix:**
  - correct the pattern;
  - anchor patterns at line starts;
  - `py_compile` the edited file, counting a syntax or import failure as "not demonstrated";
  - correct the record's line.

**4. Nit. Test gaps: each of these mutations passes all 202 tests.**
- Dropping the `NOT_A_PASS` guard (`:1194` or `:1961`): a feature-on or polls-on FAIL becomes INCONCLUSIVE when the production phase has no answer.
- Swallowing the guardrail that the undo meets after an interruption (`:1326-1332`): the run would go on after a charge signal.
- `cli.py:212-217`: dropping `*run.post_run_problems`, or dropping `run.close_sessions()`, after a second Ctrl-C.
- The `rate_limited` flag at the error-only raise site, `client_bridge.py:266`.
- RT2/RT3 "not listening" for a refused request (`:2470`), a C1 rule.
- **Fix:** one test each.

**5. Nit. When a command records more than one request, the row drops what each request got.** `proof_run.py:157-159`
- **Reproduced:** S3a with a 201 edit followed by a 403 gives INCONCLUSIVE, with request "-" and observed "no answer recorded (2 requests recorded; exactly one was expected)". No status appears, and the 201 is not undone.
- It is only reachable after an SDK change: in 9.53.0, each method I spot-checked sends one request.
- **Fix:** record each request's method, generic path and status in the row's detail, and owe the undo when any of them got a 2xx.

**6. Nit, latent. A guardrail stop from B's probe is dropped from the record.** `proof_run.py:615-625`
- When another key of the same override still reads as overridden, the harness raises `RunStopped`, and B's probe `GuardrailStop` appears nowhere, not even in `stops`.
- Today every override has one key (`matrix.py:585, 644, 662, 680`, and S15's grant), so this cannot happen yet.
- **Fix:** add the probe's stop to `stops`, and flag it as in finding 2.

**7. Nit. S15 still sends a request after a charge signal.** README line 177 and `proof_run.py:1314-1316`
- **Reproduced:** B's query answered 402, and S15's `finally` still sent the unset `PATCH …/member`.
- The README, the undo's own text ("nothing more is sent for the run's own data after a guardrail stop") and the manager's decision rationale all say nothing more is sent. C2's evidence limits do mention it.
- **Fix:** skip the unset after a guardrail stop (cleanup deletes A anyway), or state it in the README.

**8. Nit. A non-2xx read of A's stored user lets the run go on.** `proof_run.py:2229-2236`
- Nit 7's fix covers a 2xx listing without A. A non-2xx listing makes `api.require` raise, so the `result.ok` in the loop is dead code live.
- The row does become INCONCLUSIVE, through the interruption path. But the run goes on without knowing or restoring A's role (E5) or profile (S14).
- This is the reason C2's review point 1 gave for stopping the run. The verdict impact is low: running later cases with A as admin can only produce a false FAIL.
- **Fix:** catch the read's failure in E5 and S14, record INCONCLUSIVE, and defer a stop.

**9. Nit. The atomic-write claim overstates.** README line 122, and the evidence record
- Both say "every `.work` file is written through a temporary file". `usage.py:78` writes the usage ledger directly. An interrupted write fails loudly at the next load.
- **Fix:** write the ledger through `_replace`, or narrow the claim.

**10. Nit. The early-write failure note is not redacted.** `cli.py:198-200`
- The note carries `{exc}` as it is, unlike `_progress_quietly`. No exception that can reach it carries a token today, so nothing leaks. If one ever did, the leak check would refuse the final results write.
- **Fix:** `ctx.redactor.text(str(exc))`.

##### The C1 review's items and C2's own review points

| Item | Confirmed | Reason |
|---|---|---|
| F1: an interrupted case keeps its FAIL | Yes | `_observe` is called at every step I traced. `run_matrix` records one row on every exit, and a row cannot reach another case (`_partial` is reset at both ends of each case). All three review scenarios are tested. The undo follows the README's rule, and no undo is sent after a charge signal. See findings 1, 4 and 5 |
| F2: T4-rest-unread | Yes | `:1635-1657`: HOLDS (accepted, not applied) needs both controls and all three totals |
| F3: RT2/RT3 | Yes | `:2468-2486`: `input`, `not-found` and `other` are INCONCLUSIVE, and named events count only after an accepted request. The `feature` HOLDS is not reported, per the manager's decision |
| Nit 4: retry rule and call counts | Yes | Only a rate limit or a failure that is not a stop signal is retried. All four raise sites set the flag; three are tested. The README's counts match mine: 3 calls per attempt, so 6 or 12 per change. The 130-call reserve covers the measured worst case of 115 |
| Nit 5: production phase needs an answer | Yes | `:1194`, `:1961`. See finding 4 |
| Nit 6: exactly one request | Yes | `:157`, `:1781`. See finding 5 |
| Nit 7: unreadable stored user | Yes, for a 2xx listing | See finding 8 |
| Nit 8: second Ctrl-C | Yes | `cli.py:184-217` |
| Nit 9: "not verified", not "not restored" | Yes | `:603-625`, `:427-456` |
| Nit 10: credential keys | Yes | My walk of `getstream` 6.1.0's app model: 57 models and 312 field names. It finds the same seven names missed at C1, all matched now |
| C2 review points 1, 2 and 4 | Yes | Point 4's "every `.work` file" overstates (finding 9) |
| C2 review point 3 | Yes, as built | Its side effect is finding 6 |

##### Areas reviewed with no findings

- **Verdicts:** C2 added no HOLDS path; its changes only lower verdicts. The paths that HOLD without a refusal and a control of the same request are the README's documented case rules:
  - RT1;
  - RT2/RT3, where B's listening probe is the only control;
  - T4-ws;
  - E5 and S14.
- **Records:**
  - the three corrections, at evidence lines 478, 921 and 929, are accurate and marked;
  - no recorded result changed;
  - the four protected sections are byte-identical across `5fc3bea`, the head and `6a439cf`;
  - apart from findings 7 and 9, the README's rules match the code.
- **Credentials:**
  - the allowlist, the runner's refusal, redaction and the leak checks are unchanged;
  - every new output is leak-checked or redacted when created, apart from finding 10;
  - the `_key` suffix hides nothing the matrix reads, because `config_key` and the other `_key` fields are in moderation, push and app models only;
  - no replay reuses a redacted `api_key`, because only `user_id` is kept.
- **Scope:**
  - all 18 changed files are owned;
  - no dependency file, `pyproject.toml`, `.npmrc` or baseline changed;
  - all 50 files under `proofs/stream-chat/` have mode 100644, and there are no symlinks.

##### Checks run

| Check | Result |
|---|---|
| `git diff --check HEAD^1 HEAD` | No output, exit 0 |
| Installs (`env -i`, README commands) | Python 3.12.14. `getstream` 6.1.0, Ruff 0.16.8, mypy 2.3.1. `pip check`: "No broken requirements found." `npm ci`: "added 51 packages, and audited 52 packages", "found 0 vulnerabilities". stream-chat 9.53.0, ws 8.21.3, https-proxy-agent 5.0.1 |
| Unit tests | `Ran 202 tests`, `OK` |
| Ruff check / Ruff format / mypy | "All checks passed!" / "38 files already formatted" / "Success: no issues found in 37 source files" |
| `node --check` on both `.cjs` files | Exit 0; exit 0 |
| `checks/fix_reversals.py` | "reversals: 99, not demonstrated: 0", exit 0, 4 min 21 s |
| Each reversal's failure reason | 94 fail on the expected assertion or error. 3 abort on Ctrl-C by design. Reversal 8 fails only through the `SyntaxError` (finding 3) |
| 20 extra mutations | 9 caught. 7 survived as test gaps (finding 4). 4 survived on redundant or dead code |
| Secret scan of the diff (197,542 bytes) | 0 JWT-shaped strings, emails, private-key blocks, cloud or GitHub keys, TLS-weakening settings, environment dumps or secret assignments. The 53 long strings are test names and two commit SHAs |
| Reproductions against the fakes | Findings 1, 2, 5 and 7. Reversal 8 at `e85bba0` and at the head |
| Repository state | `git status` is empty. Only ignored paths were created, and no `.work/` |

##### Limits

- Nothing was exercised live.
- I did not read hosted CI.
- The secret scan could not look for the application's API key, because its variable is absent (OD-28).
- I reviewed the rest of the harness only where C2 changed it. Findings 1 and 2 are C1's code, inside functions C2 changed, and the prompt's focus questions ask about both.
- I used no sub-agents.
- **The manager's decisions:** I agree with both.
  - For the RT2/RT3 change, the session making it should also decide whether an `auth` or `permission` refusal needs a control of the same request. RT3 could use B's own `markRead`. RT2 has no production control, because typing is off.
- I changed nothing in the repository, on GitHub or in Notion.

**NOTHING NEEDED.** Relay this to App Manager 3.

#### Manager verification of the review (App Manager 3, 26 September 2026)

The session committed nothing, so there is no branch to check. The manager checked the report's claims against the reviewed head.

- **Classification.** The manager's own run of the three classifications before the review gave the same results: 109 paths, full scope; 24 paths, full scope, with nothing outside `proofs/stream-chat/`; 6 Markdown paths, `ordinary-docs-only`.
- **Findings, at `63e922f`:**
  - **Finding 1:** `if not on.ok` makes the verdict INCONCLUSIVE whatever the feature-on phase observed (`proof_run.py:1187-1189`).
  - **Finding 2:** `cmd_run` skips cleanup only when the run's own stop was a "stopping at once" `GuardrailStop` (`cli.py` around line 176); `finish()` cleans up whenever it is asked to, whatever its restores met.
  - **Finding 3, reproduced:** on a scratch copy of `cli.py`, the reversal's 8-space pattern matches inside the 12-space line `problems = run.finish(…)`, and the reverted file fails to compile with "expected 'except' or 'finally' block". The manager's verification of C2 quoted the script's summary without checking each reversal's failure reason, and told Nathan that all 99 were demonstrated (AM3-18). The real count is 98 of 99; the fix it reverts is still tested.
  - **Finding 8:** `_server_user` wraps the read in `api.require`, which raises on a non-2xx answer, so its `result.ok` test cannot be false (`proof_run.py:2229-2236`).
  - **Finding 9:** `usage.py`'s `save()` writes the ledger directly.
  - **Finding 10:** the early-write note interpolates the exception unredacted (`cli.py:198-200`).
- **Not re-run by the manager:** the session's installs, tests, reversal runs, 20 mutations and reproductions of findings 1, 2, 5 and 7. Its installs, tests and reversal summary match the manager's own run on C2's head.

#### Disposition

- **C2's code head `63e922f` is approved.**
- **A third offline correction pass, P06.1-C3, comes before I2a's live runs.** It makes:
  - the RT2 and RT3 change the manager decided on C2, with the reviewer's point settled by the brief's matrix quality rule: an `auth` or `permission` refusal gives HOLDS only when a control of the same request, by a member allowed to make it, succeeded. For RT3 that is B's own `markRead` with the same body. For RT2 none exists while typing is off, so such a refusal is INCONCLUSIVE;
  - findings 1 and 2, and nits 3 to 10.

  Finding 2 is the guard that keeps the run from sending requests after a charge signal, which Nathan's $0 budget depends on (OD-12), and finding 1 can hide an observed FAIL. Both are fixed before live budget is spent.
- **C3's exact-head review follows,** scoped to C3's change. To bound the rounds: after it, only a blocking finding, or a should-fix finding that could create a false HOLDS, lose an observed FAIL or send a request after a charge signal, delays I2a. Other findings go into I2a's offline first step or the final delta review.

## P06.1-C3 corrections

The third correction pass on the harness. It makes the manager's RT2 and RT3 decision on C2, and fixes the C2 review's findings 1 and 2 and nits 3 to 10. It made no Stream call and ran none of the harness's live commands. The first live use of these fixes, and of C1's and C2's, is in P06.1-I2a.

- **Prompt:** revision 1, from commit `e5180ab40623858ffd00471f0747e948534418e7`.
- **Branch:** `claude/friendly-hypatia-ug6r52`. **Start:** `e5180ab40623858ffd00471f0747e948534418e7`.
- **Code head:** `a5e222100e8673d07a533d2eddc04aa21248b02e`. It carries every code change and the records corrected below, and every check below ran on it. The commit that adds this section changes only this record.
- **Date:** 26 September 2026.

### Environment and start gate

| Check | Result |
|---|---|
| `DATABASE_URL`, `HD_API_KEY`, `GEO_API_KEY` | None present (the check printed nothing) |
| `STREAM_APP_ID`, `STREAM_API_KEY`, `STREAM_API_SECRET` | None present (the check printed nothing) |
| `command -v node npm npx python3.12` | `/root/.local/bin/node`, `/root/.local/bin/npm`, `/root/.local/bin/npx`, `/root/.local/bin/python3.12` |
| Versions | node v24.19.0; npm 11.9.0; Python 3.12.14 |
| Start gate | `git fetch origin claude/stoic-carson-66gdig`; `git merge --ff-only e5180ab…` fast-forwarded from `0f45e64`; `git rev-parse HEAD` printed `e5180ab40623858ffd00471f0747e948534418e7`; `git diff --stat 63e922f… HEAD -- proofs/stream-chat/` printed nothing |

The environment was never dumped. There were no connections to Stream, a database, HDE or Railway, and no `playwright install`, `eas` or `migrate`. Installs got the proxy and CA variables by reference.

### The RT2 and RT3 change, findings 1 and 2, and nits 3 to 10

Paths are under `proofs/stream-chat/`, and line numbers are at the code head. Each test named fails with its fix reverted and passes with it (see "Checks", item 5). The suggested fix was used for every item unless the row says otherwise.

| Item | Status | Where | Tests |
|---|---|---|---|
| RT2 and RT3 (the manager's decision on C2) | Fixed. <br>**Feature refusal:** a 400 feature error (code 18 or 19) is REFUSED (feature off; not a permission error), as for every other case (`glow_stream_proof/proof_run.py:2673`). <br>**Authentication or permission refusal:** HOLDS only when the case's control succeeded and nothing carrying the marker reached B while B was listening (`:2690`). The control is the same request by a member allowed to make it, and its recorded method and path must equal A's (from the independent review, point 4); if they differ, the case is INCONCLUSIVE, "the positive control was another request" (`:2698`). <br>**RT3's control:** B's own `markRead` with the same body (`matrix.py:856`). It is sent after both windows are collected and kept (`:2620`, `:2646`). Its own events are collected apart (`:2651`), recorded by type (`control_event_types`) and never searched for the marker (`:2652`). A control that does not succeed leaves the case INCONCLUSIVE (`:2704`). <br>**RT2:** has none, because no member may send a typing event while typing is off (`matrix.py:840`), so its authentication or permission refusal is INCONCLUSIVE, "no positive control" (`:2682`). <br>`input`, `not-found` and `other` stay INCONCLUSIVE. README "Verdict rules", RT2 and RT3. I1's recorded RT2 stays as recorded | `tests/test_answers.py`: `PayloadRefusalAttributionTest` (six new tests: feature refusals, RT2 without a control, RT3 with B's request, B's request refused, B's request to another path, and the control's own events) and `RequestUnderTestInCasesTest.test_rt2_feature_refusal_is_refused_feature_not_holds`. `tests/test_interruptions.py` `ProceduresKeepWhatTheyObservedTest.test_rt3_marker_after_the_probe_survives_the_control_ending` |
| 1. A feature-gated case's observed FAIL becomes INCONCLUSIVE when the enabling request was not 2xx | Fixed: `if not on.ok and result.verdict != matrix.FAIL:` (`:1257`) | `tests/test_answers.py` `FeatureOnFailTest`: S2 and S12 with a failed enabling request, and the INCONCLUSIVE case without an observed FAIL |
| 2. A charge or limit signal first met during the end of the run does not skip cleanup | Fixed, and recorded where it is met, beyond the suggested flag, after the independent review (points 1 and 3). <br>**Where a signal is recorded:** the server client's two checks (`server_api.py:107`, `:149`) and a client session's two (`client_bridge.py:257`, `:264`) raise through `UsageLedger.stop_at_once` (`usage.py:94`). It records the stop in the run's ledger (`usage.py:76`) before it is raised, and marks it `at_once` (`usage.py:53`). So no later exception can lose it: not another stop kept as the run's stop, and not a Ctrl-C or error that replaces it in flight. <br>**The run's record:** `ProofRun.stop_signals` (`proof_run.py:369`) reads that record. `record_signal` (`:386`) adds any at-once stop not raised through the ledger, where the run's own stop (`cli.py:178`), a restore (`:471`), B's probe (nit 6), the cleanup and the final configuration read (`:3041`) meet one. A signal met by the cleanup also ends it at once (`:2850`). <br>**The end of the run:** `finish()` still restores and re-reads the configuration, but after any recorded signal it skips the cleanup and closes the client processes (`:3028`). The problem reads "cleanup skipped: a charge or limit signal stopped the run at once (…); check it, then run cleanup --apply". `cmd_run` passes `finish()` whether cleanup is needed (`cli.py:206`) and no longer decides from its own stop. <br>**After a recorded signal, whatever is in flight:** <br>• the run stops once the case's row is recorded, when the error in flight is one after which the run would go on (`:1117`); <br>• neither the undo of a client success (`:1405`) nor S15's unset (`:2184`) is sent. <br>README "Budget guardrails" and the end-of-run sequence | `tests/test_stop_signals.py`: `SignalRecordTest` (four tests), `SignalReplacedInFlightTest` (two) and `MemberFieldUnsetTest.test_no_unset_after_a_signal_whose_stop_is_not_in_flight`. <br>`tests/test_cli.py` `CommandTest`: the review's reproduction, three rate-limited retries, the run's own stop, a stop replaced by a Ctrl-C, and a budget stop that still cleans up. <br>`tests/test_interruptions.py` `ReviewScenariosTest.test_no_undo_after_a_signal_whose_stop_an_error_replaced`. <br>`tests/test_temporary_changes.py` `FinishTest`. <br>`tests/test_server_api.py` `StopAtOnceFlagTest`. <br>`tests/test_client_session.py` `ClientRateLimitFlagTest.test_every_client_signal_stops_at_once` |
| Nit 3. C1's reversal "F2 end of run" no longer reverts its fix | Fixed. <br>**The pattern:** now the 12-space line (`checks/fix_reversals.py:188`). <br>**Anchoring:** a pattern counts only where it starts a line, and must occur there exactly once (`anchored`, `:1746`; `main`, `:1831`). At the start, ten of the 99 reversals had a pattern that began inside a longer line. Nine still reverted their fix (the C2 review found their tests failing on the expected assertion or error); "F2 end of run" did not. All ten are now anchored. <br>**Loading:** every edited file must compile and import (`.py`) or pass `node --check` (`.cjs`), or the reversal is "not demonstrated" (`loads`, `:1757`). <br>**Output:** the script prints each failing test with the exception its failure ended in (`failure_reasons`, `:1782`). <br>The record's "C1's two Ctrl-C ones" is corrected below | `tests/test_fix_reversals.py` `FixReversalsTest` (five tests, including every pattern in the table and every test it names) |
| Nit 4. Seven mutations passed all 202 tests | Fixed: one test each. <br>**`NOT_A_PASS` guard, feature-on:** `ProductionPhaseAnswerTest.test_feature_on_fail_survives_a_production_request_without_an_answer`. <br>**`NOT_A_PASS` guard, polls-on:** `test_polls_on_fail_survives_a_production_vote_without_an_answer`. <br>**The guardrail the undo meets after an interruption:** `ReviewScenariosTest.test_a_guardrail_met_by_the_undo_after_an_interruption_stops_the_run`. <br>**`*run.post_run_problems` after a second Ctrl-C:** `CommandTest.test_second_ctrl_c_keeps_the_problems_finish_found`. <br>**`run.close_sessions()` after a second Ctrl-C:** `test_second_ctrl_c_closes_the_client_sessions`. <br>**`rate_limited` at the error-only raise site:** `ClientRateLimitFlagTest.test_the_error_only_check_flags_a_rate_limit`. <br>**RT2/RT3 "not listening" for a refused request:** `PayloadRefusalAttributionTest.test_a_refusal_while_b_is_not_listening_is_inconclusive`. <br>Each has a reversal | As listed |
| Nit 5. A command with more than one request loses what each got | Fixed. The case's row lists each such command's requests, with each request's method, generic path and status (`requests`; `_send` `:408`; `_result` `:1144`; reset for each case `:1092`). In a generic case, a 2xx to any of its requests owes the undo, and a poll or user group it created is tracked for cleanup (`:1290`). After the independent review (point 2), the production phase of a feature-gated case lists its command too, and undoes a 2xx among its requests (`:1246`, `:1253`) | `tests/test_answers.py` `OneRequestTest` (three new tests) and `ProductionPhaseAnswerTest.test_a_production_command_with_several_requests` |
| Nit 6. B's probe stop dropped | Fixed. When a key still reads as overridden, B's probe stop is kept in `stops` and its signal recorded (`:666`) | `tests/test_stop_signals.py` `ProbeStopKeptTest` |
| Nit 7. S15 sends its unset after a charge signal | Fixed with the first suggested fix. After a guardrail stop, S15 sends no unset of A's member field (`_unsetting_member_field`, `:2170`), and since the independent review (point 3) none after a recorded signal either (`:2184`). The run's notes, and the row's `member_field_unset` once the case has observed something, say so. Cleanup deletes A; after a charge or limit signal that is `cleanup --apply`. After any other interruption the unset is still sent. README S15 and "Limits" | `tests/test_stop_signals.py` `MemberFieldUnsetTest` (four tests) |
| Nit 8. A non-2xx read of A's stored user lets the run go on | Fixed, and extended. A read that Stream does not answer with 2xx is caught in E5 and S14: the case is INCONCLUSIVE, "A's stored user could not be read", and the run stops once the row is recorded (`_stored_user`, `:2364`). A guardrail stop on the read is not caught; it is the run's stop. A 2xx listing without A now also stops the run, for the same reason: A's stored role or profile is unknown | `tests/test_procedures.py` `StoredUserReadFailureTest` (three tests); `StoredUserUnreadableTest` now expects the stop |
| Nit 9. The ledger is not written atomically | Fixed with the first suggested fix: the ledger is written through `_replace`, like every `.work` file (`usage.py:92`) | `tests/test_usage_and_report.py` `UsageTest.test_an_interrupted_save_leaves_the_previous_ledger_whole` |
| Nit 10. The early-write failure note is not redacted | Fixed: `ctx.redactor.text(str(exc))` (`cli.py:200`) | `tests/test_cli.py` `CommandTest.test_the_early_write_failure_note_is_redacted` |

C1's and C2's own tests changed in six places, each to the new rule or to check more:
- **Replaced for the manager's decision:** `PayloadRefusalAttributionTest.test_attributable_refusals_hold` and `RequestUnderTestInCasesTest.test_rt2_refused_by_stream_with_nothing_delivered_holds` asserted HOLDS on a feature refusal. The tests in the RT2 and RT3 row replace them.
- **`PayloadRefusalAttributionTest`'s helpers:** they set up B's control and record the path stream-chat sends `markRead` or `sendEvent` to.
- **`FinishTest`** records the signal and calls `finish(cleanup=True)` (finding 2).
- **`StoredUserUnreadableTest`** expects the run to stop after the row, and the E5 test checks the stop (nit 8).
- **`ClientRateLimitFlagTest.test_flags`** uses the helper that now takes a script; its assertions are unchanged.
- **`GuardedUnsetTest`'s docstring** says which unset it now exercises (the independent review, point 5).

### The independent review of these corrections

A read-only sub-agent reviewed the diff adversarially while it was being written. It reproduced its points against the fakes in scratch copies and made no Stream call. I verified each point.

1. **A Ctrl-C that replaced a signal's stop lost the signal.** E5's own client session met a rate limit on connect, and a Ctrl-C arrived while E5's `finally` closed that session. The run's record was empty, and the cleanup sent both hard deletes. Fixed: the server client and the client sessions record a signal in the run's ledger as they raise its stop (finding 2's row). Tests: `CommandTest.test_a_signal_whose_stop_a_ctrl_c_replaced_skips_the_cleanup`, `SignalReplacedInFlightTest`.
2. **The production phase of a feature-gated case lost nit 5's detail and undo.** S5's production command recorded a 201 and then a 403. The row listed neither, and the 201 was not undone. Fixed (nit 5's row). Test: `ProductionPhaseAnswerTest.test_a_production_command_with_several_requests`.
3. **S15's unset and the undo after an interrupted control decided from the exception in flight, not from the run's record** (latent).
   - When another key still reads as overridden, B's probe after a removal records its signal but raises `RunStopped`, so S15's unset was still sent.
   - S15's override has one key today, so this could not happen yet. The reviewer found no path to the undo.
   - Fixed: neither is sent once a signal is recorded (`:2184`, `:1405`).
   - Tests: `MemberFieldUnsetTest.test_no_unset_after_a_signal_whose_stop_is_not_in_flight` and `ReviewScenariosTest.test_no_undo_after_a_signal_whose_stop_an_error_replaced`.
4. **RT3's control was not matched to A's request** (optional).
   - HOLDS rested on the identical step and the one-request rule.
   - Fixed: the control counts only if its recorded method and path equal A's (`:2690`); otherwise the case is INCONCLUSIVE (`:2698`). The tests' fakes now record the paths stream-chat 9.53.0 sends `markRead` and `sendEvent` to.
   - Test: `PayloadRefusalAttributionTest.test_rt3_control_that_was_another_request_is_inconclusive`.
5. **Some of finding 2's reversals show fallbacks, not the production path** (left as they are, recorded here).
   - Every production charge or limit stop now comes through `UsageLedger.stop_at_once`. So these only add stops raised elsewhere: the `record_signal` calls in `_restore`, `cleanup()`, the final configuration read and `cmd_run`, and `at_once = at_once or rate_limited`. Their reversals are demonstrated with fakes that raise such stops directly.
   - The production chain is shown by "C3 review: the ledger records a signal as its stop is raised" and the four raise-site reversals.
   - Five C1 and C2 tests raise charge-like stops without `at_once`. The reviewer listed four; `RateLimitRetryTest.test_a_charge_signal_is_not_retried` is the fifth. None of their assertions depends on the flag.
   - `GuardedUnsetTest` passed on the production phase's failing unset, not the control's; its docstring now says so.

The reviewer also confirmed, on the tree it reviewed:
- no new HOLDS path, and no path that downgrades an observed FAIL;
- no `except Exception` on the run's path that swallows a `GuardrailStop`;
- RT3's control is the same request. stream-chat 9.53.0's `markRead` sends one `POST …/read`, or nothing without read events and the capability. Mark-delivered requests need `delivery_events`, which the match type turns off;
- all 144 reversals in the table it reviewed fail when reverted and pass when restored, none through a SyntaxError or ImportError.

### Records corrected

In this record, each claim was already false at C2's head. Each is corrected in place and marked "(corrected in P06.1-C3)". No recorded result changed, and the six sections the prompt protects are unchanged byte for byte.

- **C2's nit 7 row:** `_server_user` returning `None` held for a 2xx listing only. A listing Stream did not answer with 2xx made `ServerApi.require` raise, so the row read "harness error" and the run went on; the fakes' `require` does not raise, which hid it (the C2 review's nit 8).
- **C2's review point 4:** "every `.work` file is written through a temporary file" did not hold for the usage ledger (nit 9).
- **C2's "Checks" row 5:** it read "C1's two Ctrl-C ones". C1 had one Ctrl-C reversal. The fourth reversal that ended without a test report was C1's "F2 end of run", which failed only because the edited `cli.py` did not compile, so 98 of the 99 were demonstrated (nit 3).
- **C2's "Decisions", the undo bullet:** "a charge or limit signal … deletes none of its data" held only for a signal that was the run's own stop (finding 2).
- **C2's "What P06.1-I2a must know", outputs:** `.work` files were written through a `.partial` file, except the usage ledger (nit 9).

In `proofs/stream-chat/README.md`, each rule as the code now applies it, with the changed ones marked:
- RT2 and RT3, including the control's method and path;
- the one-request rule's `requests` detail and its undo, in both phases of a feature-gated case;
- feature-gated cases whose enabling request failed;
- E5's and S14's stop on an unreadable stored user;
- the undo after an interrupted control, and S15's unset, after a recorded signal;
- the interrupted-case rule after a signal whose stop an error replaced;
- the end-of-run cleanup rule and `stop_signals`;
- the charge-signal paragraph: where a signal is recorded, and what the run then sends;
- the restore and probe-stop paragraphs;
- the atomic ledger and the redacted early-write note;
- exit code 4;
- the `checks/fix_reversals.py` rules;
- the limits added in P06.1-C3.

### Checks

Run from `proofs/stream-chat/` unless noted, at code head `a5e2221`, in clean processes (`env -i`), with no `STREAM_*` variable present.

| # | Check | Result |
|---|---|---|
| 1 | `git diff --check e5180ab… a5e2221` (repository root) | No output, exit 0 |
| 1 | `git diff --name-only e5180ab… a5e2221` | 19 paths: this record and 18 under `proofs/stream-chat/`, two of them new (`tests/test_stop_signals.py`, `tests/test_fix_reversals.py`). All owned. No dependency file, `.npmrc`, `pyproject.toml` or baseline change. All 52 files under `proofs/stream-chat/` have mode 100644; there is no symlink or executable. +2,400 and −175 lines |
| 2 | The trusted policy from `origin/main` (`0f45e64`), extracted to a directory outside the tree and run with system Python 3.11.15: `python3 -I change_scope.py --base e5180ab… --head a5e2221… --merge-base` | Exit 0; `{"full": true, "reason": "behavior-or-empty", …}`, 19 paths. One merge base, `e5180ab`. Full scope, as expected |
| 3 | In a new directory, from the unchanged lock files: `python3.12 -m venv .venv`; `pip install --require-hashes -r requirements-dev.lock`; `pip check`; `npm ci --ignore-scripts`. Proxy and CA variables were passed by reference | Python 3.12.14. "No broken requirements found." `getstream` 6.1.0, Ruff 0.16.8, mypy 2.3.1. npm: "added 51 packages, and audited 52 packages", "found 0 vulnerabilities". `stream-chat` 9.53.0, `ws` 8.21.3, `https-proxy-agent` 5.0.1 |
| 4 | `env -i PATH="$PATH" HOME="$HOME" LANG=C.UTF-8 .venv/bin/python -m unittest discover -s tests -t .`, on a clean export of each commit using that install | At the start (`e5180ab`): `Ran 202 tests`, `OK`. At the code head: `Ran 252 tests`, `OK` |
| 4 | `.venv/bin/ruff check .` / `.venv/bin/ruff format --check .` | "All checks passed!" / "40 files already formatted" |
| 4 | `.venv/bin/mypy` | "Success: no issues found in 39 source files" |
| 4 | `node --check client/runner.cjs`; `node --check client/error-info.cjs` | Exit 0; exit 0 |
| 5 | `.venv/bin/python checks/fix_reversals.py <scratch dir>` | At the start (`e5180ab`, its own script): "reversals: 99, not demonstrated: 0", exit 0; but C1's "F2 end of run" failed only because the edited `cli.py` did not compile (nit 3), so 98 of the 99 were demonstrated. At the code head: "reversals: 147, not demonstrated: 0", exit 0, in 617 s: C1's 51, C2's 48 and 48 for C3 (the RT2 and RT3 change, findings 1 and 2, nits 3 to 10, and the independent review's points 1 to 4). Every edited file loaded, and no reversal failed through a SyntaxError or an import error. 124 failed on an assertion, and 20 on the error the reverted fix causes, for example a `KeyError` on a missing detail, `RunStopped` where a guardrail stop was expected, or a `JSONDecodeError` on a truncated file. Three failed because a Ctrl-C aborted the test process, by design: C1's "F2 Ctrl-C handled", and C2's "nit 8 second Ctrl-C inside finish()" and "a Ctrl-C during the early write still reaches the restores". "Each fix reversal at the code head" below lists every reversal and how its tests failed. The checkout was unchanged afterwards |
| 6 | Secret scan of `git diff e5180ab… a5e2221` (204,608 bytes) | JWT-shaped strings 0; email addresses 0; private-key blocks 0; AWS-style keys 0; GitHub or other token formats 0; the application's API key 0; TLS-weakening settings 0; environment dumps 0; no secret or token assignment in added lines. The 53 long token-like strings are 51 test names, one test helper's name and a separator line |
| – | The six protected sections of this record, compared with `e5180ab` | Byte-identical |

Not run: any live command; hosted CI (this session opened no pull request and triggered nothing).

#### Each fix reversal at the code head

From `checks/fix_reversals.py`'s output at `a5e2221`, in its order. Each reversal failed as listed with its fix reverted and passed with the fix restored. Long reasons are cut at 150 characters, and at most three failing tests are shown per reversal.

| # | Reversal | How its tests failed with the fix reverted |
|---|---|---|
| 1 | F1 request under test (generic) | `test_sdk_error_without_a_request_has_no_answer`: AssertionError: 'permission' != 'no-response'; `test_generic_case_uses_the_record_not_the_sdk_error`: AssertionError: 'HOLDS' != 'FAIL'; `test_generic_case_without_a_request_is_inconclusive`: AssertionError: 'HOLDS' != 'INCONCLUSIVE' |
| 2 | F1 G1 | `test_g1_fails_whenever_the_clients_post_guest_created_a_guest`: AssertionError: 'HOLDS' != 'FAIL' |
| 3 | F1 G3 | `test_g3_is_inconclusive_unless_the_anonymous_connect_succeeded`: AssertionError: 'anonymous connect' not found in 'no answer recorded (error: rethro… |
| 4 | F1 RT2/RT3 | `test_rt2_local_throw_is_inconclusive`: AssertionError: 'refusal not attributable (no-response)' != 'no answer from Stream was recorded for the reque…; `test_rt3_null_return_without_a_request_is_inconclusive`: AssertionError: 'refusal not attributable (no-response)' != 'no answer from Stream was reco… |
| 5 | F2 RunStopped re-raised | `test_failed_restore_stops_the_run`: AssertionError: RunStopped not raised |
| 6 | F2 try before enabling (type/channel) | `test_journal_entry_exists_before_the_enabling_request`: AssertionError: True is not False |
| 7 | F2 try before enabling (guest) | `test_guest_creation_is_restored_after_an_interrupt_before_the_control`: AssertionError: False is not True |
| 8 | F2 guardrail in flight kept | `test_restore_failure_does_not_hide_a_guardrail_stop_in_flight`: glow_stream_proof.proof_run.RunStopped: could not restore glow-match features {'cust… |
| 9 | F2 end of run: journal, cleanup, verify, exit | `test_configuration_difference_after_the_run_exits_non_zero`: AssertionError: 0 != 4; `test_cleanup_problem_exits_non_zero`: AssertionError: 0 != 4; `test_ctrl_c_restores_cleans_up_writes_results_and_exits_non_zero`: AssertionError: Lists differ: ['guest user creation enabled'] != [] |
| 10 | F2 Ctrl-C handled | the test process stopped before reporting: KeyboardInterrupt |
| 11 | F3 exactly one | `test_no_dashboard_user_stops_the_run_when_one_is_expected`: IndexError: list index out of range; `test_two_dashboard_users_stop_the_run`: AssertionError: RunStopped not raised |
| 12 | F3 created_at | `test_another_creation_time_stops_the_run`: AssertionError: RunStopped not raised |
| 13 | F4 local events dropped | `test_local_query_event_is_not_counted_as_delivered`: AssertionError: True is not false; `test_marker_only_in_a_local_event_is_not_delivered`: AssertionError: 'FAIL' == 'FAIL' |
| 14 | nit 1 every window | `test_marker_in_another_event_type_in_the_second_window_fails`: AssertionError: 'HOLDS (accepted, not applied)' != 'FAIL' |
| 15 | nit 1 every event type | `test_marker_in_another_event_type_in_the_second_window_fails`: AssertionError: 'HOLDS (accepted, not applied)' != 'FAIL' |
| 16 | F5 reply id checked | `test_mismatched_reply_ends_the_session`: AssertionError: ClientSessionEnded not raised |
| 17 | F5 timeout ends session | `test_timeout_ends_the_session_and_releases_the_connection`: RuntimeError: no reply within 0.5s |
| 18 | F5 buffered line (select reader) | `test_buffered_line_is_read_without_a_timeout`: glow_stream_proof.client_bridge.ClientSessionEnded: client fake ended: no reply within 1.0s |
| 19 | F6 simulation guest connect refused | `test_guest_reach_is_not_run_when_the_guest_connect_is_refused`: AssertionError: 'guest connect 403 / code 17' not found in 'identical request with g… |
| 20 | F7 leak terms | `test_channel_object_without_text_is_a_leak`: AssertionError: 'INCONCLUSIVE' != 'FAIL'; `test_terms`: AssertionError: '{AB}' not found in {'{m_a_text}', '{m_b_text}'} |
| 21 | nit 2 code 2 | `test_api_key_error_is_not_a_token_refusal`: AssertionError: 'auth' != 'other' |
| 22 | nit 3 user_id from params | `test_no_user_id_is_not_invented`: AssertionError: 'user_id' unexpectedly found in 'POST /channels/glow-match/{XD}/query ?user_id={X}' |
| 23 | nit 4 undo checked | `test_failed_undo_stops_the_run_after_its_case`: AssertionError: RunStopped not raised |
| 24 | nit 4 member field unset checked | `test_member_field_unset_is_checked`: AssertionError: RunStopped not raised |
| 25 | nit 4 removal re-read | `test_removal_that_did_not_apply_stops_the_run`: AssertionError: RunStopped not raised |
| 26 | nit 4 removal status checked | `test_removal_refused_stops_the_run`: AssertionError: RunStopped not raised |
| 27 | nit 5 cleanup steps guarded | `test_a_failing_step_does_not_stop_the_others`: RuntimeError: connection reset |
| 28 | nit 5 task status judged | `test_task_that_does_not_complete_is_a_problem`: AssertionError: "channels_task is 'failed', not 'completed'" not found in [] |
| 29 | nit 6 typed-call charge signal | `test_typed_calls_stop_on_a_charge_signal`: KeyError: 'duration' |
| 30 | nit 7 request op removed | `test_unused_request_op_is_gone`: AssertionError: "Both secret and user tokens are not set.[68 chars]lled" != 'unknown op request' |
| 31 | nit 8 baseline written without users | `test_baseline_writes_no_other_users_identifier_or_name`: AssertionError: 'private-user-id' unexpectedly found in '{"app": {"app": {"id": 1729640, "d… |
| 32 | nit 8 redaction by pattern | `test_sensitive_keys_are_matched_by_pattern`: AssertionError: 'plain' != '<redacted-secret>' |
| 33 | nit 9 verify required settings | `test_verify_checks_permission_version_and_member_custom_settings`: AssertionError: False is not true : permission_version |
| 34 | nit 10 restore verified | `test_restore_apply_verifies_what_it_restored`: AssertionError: 0 != 1 |
| 35 | nit 11 isomorphic-ws check | `test_stream_chat_uses_the_runners_websocket`: AssertionError: False is not true : {'id': 1, 'ok': False, 'data': None, 'error': {'status': None, 'co… |
| 36 | nit 12 cleanup reserve | `test_reserve_covers_the_worst_case_end_of_run`: AssertionError: 115 not less than or equal to 60 |
| 37 | nit 13 client-created data tracked | `test_client_created_poll_and_group_are_deleted`: AssertionError: '/polls/client-poll' not found in {'/polls/p1'} |
| 38 | nit 13 verify-clean lists polls and groups | `test_verify_clean_lists_polls_and_user_groups`: KeyError: 'remaining_polls' |
| 39 | nit 15 check evidence redacted | `test_check_evidence_is_redacted`: AssertionError: '<jwt>' unexpectedly found in 'got <jwt>' |
| 40 | nit 16 E5 connection role | `test_e5_role_carried_by_the_connection_fails`: AssertionError: 'HOLDS (accepted, not applied)' != 'FAIL' |
| 41 | nit 16 S14 connection profile | `test_s14_profile_carried_by_the_connection_fails`: AssertionError: 'INCONCLUSIVE' != 'FAIL' |
| 42 | nit 16 T4-rest-unread controls | `test_unread_refusal_without_its_controls_is_inconclusive`: AssertionError: 'HOLDS' != 'INCONCLUSIVE' |
| 43 | review 1: a re-read proves a removal only if it showed the override | `test_re_read_that_never_shows_the_override_is_recorded_not_verified`: AssertionError: "not verified: ['replies']" not found in 'override removed (20… |
| 44 | review 1: an ended B session leaves the grant unverified | `test_grant_unverifiable_when_bs_session_has_ended`: glow_stream_proof.proof_run.RunStopped: restore failed: config_overrides ['grants'] on AB: Clien… |
| 45 | review 2: a failed restore keeps the observed row | `test_failed_restore_stops_the_run`: AssertionError: 'interrupted before the case finished: the run stopped during this case' != 'the restore failed … |
| 46 | review 3: S15's unset never hides a guardrail stop | `test_guardrail_stop_survives_a_failing_unset`: AssertionError: GuardrailStop not raised |
| 47 | review 4: polls and groups present at preflight are not leftovers | `test_only_new_ones_are_leftovers`: AssertionError: Lists differ: ['older-poll', 'run-poll'] != ['run-poll'] |
| 48 | review 5: journalled restores are retried | `test_restore_is_retried`: AssertionError: 1 != 3 |
| 49 | review nit: an unanswered anonymous connect is not a KeyError | `test_later_probes_are_inconclusive`: AssertionError: 'the anonymous connect did not answer' not found in "harness error: KeyError: 'anonymous'" |
| 50 | review nit: verify_restored checks automod and message length | `test_verify_restored`: AssertionError: Lists differ: [] != ['team.max_message_length is 1, want 5000'] |
| 51 | review nit: runner reports ws-api only for Stream's frame | `test_kinds`: AssertionError: 'ws-api' != 'ws-failure' |
| 52 | C2 F1 an interrupted case keeps what it observed | `test_s2_fail_survives_a_timeout_in_the_production_phase`: AssertionError: 'INCONCLUSIVE' != 'FAIL'; `test_s15_leak_survives_bs_session_ending_during_the_control`: AssertionError: 'INCONCLUSIVE' != 'FAIL'; `test_s3a_fail_is_recorded_when_the_replay_hits_a_rate_limit`: AssertionError: 'INCONCLUSIVE' != 'FAIL'; and 17 more |
| 53 | C2 F1 a guardrail stop records the case | `test_guardrail_stop_with_nothing_observed_records_an_inconclusive_row`: AssertionError: []; `test_s3a_fail_is_recorded_when_the_replay_hits_a_rate_limit`: AssertionError: []; `test_guardrail_stop_survives_a_failing_unset`: AssertionError: Lists differ: [] != ['S15'] |
| 54 | C2 F1 Ctrl-C records the case | `test_ctrl_c_with_nothing_observed_records_an_inconclusive_row`: AssertionError: []; `test_s3a_undo_is_not_made_after_ctrl_c`: AssertionError: [] |
| 55 | C2 F1 the owed undo after an interrupted control | `test_s3a_fail_is_recorded_when_the_replay_hits_a_rate_limit`: KeyError: 'client_success_undo'; `test_s3a_client_success_is_undone_after_a_replay_error`: KeyError: 'client_success_undo'; `test_s3a_undo_is_not_made_after_ctrl_c`: KeyError: 'client_success_undo' |
| 56 | C2 F1 no undo after a guardrail stop | `test_s3a_fail_is_recorded_when_the_replay_hits_a_rate_limit`: AssertionError: False is not true |
| 57 | C2 F1 the undo after a completed control is recorded | `test_undo_after_a_completed_control_is_recorded`: KeyError: 'client_success_undo' |
| 58 | C2 F1 kept: the client's request before its control | `test_s3a_fail_is_recorded_when_the_replay_hits_a_rate_limit`: AssertionError: 'INCONCLUSIVE' != 'FAIL'; `test_an_observed_refusal_becomes_inconclusive_with_the_interruption_as_reason`: AssertionError: 'not judged: client X ended: no reply within 60s' !=… |
| 59 | C2 F1 kept: the feature-on phase (S2) | `test_s2_fail_survives_a_timeout_in_the_production_phase`: KeyError: 'feature_override' |
| 60 | C2 F1 kept: bad-token REST | `test_t2_rest_success_survives_as_controls_session_ending`: AssertionError: 'INCONCLUSIVE' != 'FAIL' |
| 61 | C2 F1 kept: bad-token WebSocket | `test_t4_ws_connection_as_b_survives_a_failed_disconnect`: AssertionError: 'INCONCLUSIVE' != 'FAIL' |
| 62 | C2 F1 kept: T4-rest-xd | `test_t4_rest_xd_success_survives_xs_session_ending`: AssertionError: 'INCONCLUSIVE' != 'FAIL' |
| 63 | C2 F1 kept: G1 | `test_g1_created_guest_survives_a_failed_disconnect`: AssertionError: 'INCONCLUSIVE' != 'FAIL' |
| 64 | C2 F1 kept: guest and anonymous probes | `test_g3_leak_survives_the_controls_session_ending`: AssertionError: 'INCONCLUSIVE' != 'FAIL' |
| 65 | C2 F1 kept: S10 with polls on | `test_s10_vote_success_survives_an_error_in_the_server_replay`: AssertionError: 'INCONCLUSIVE' != 'FAIL' |
| 66 | C2 F1 kept: S10 before the production vote | `test_s10_polls_on_control_survives_the_production_vote_ending`: AssertionError: 'control not completed' != 'server replay POST -> 201' |
| 67 | C2 F1 kept: S15 under production | `test_s15_leak_survives_bs_session_ending_during_the_control`: AssertionError: 'INCONCLUSIVE' != 'FAIL' |
| 68 | C2 F1 kept: S14's connection | `test_s14_profile_on_the_connection_survives_a_failed_disconnect`: AssertionError: 'INCONCLUSIVE' != 'FAIL' |
| 69 | C2 F1 kept: S14's stored state | `test_s14_stored_change_survives_an_error_in_the_control`: AssertionError: 'INCONCLUSIVE' != 'FAIL' |
| 70 | C2 F1 kept: E5's connection | `test_e5_role_on_the_connection_survives_a_failed_disconnect`: AssertionError: 'INCONCLUSIVE' != 'FAIL' |
| 71 | C2 F1 kept: RT2/RT3 first window | `test_rt2_marker_in_the_first_window_survives_bs_session_ending`: AssertionError: 'INCONCLUSIVE' != 'FAIL' |
| 72 | C2 F1 kept: RT1 | `test_rt1_xd_event_survives_xs_session_ending`: AssertionError: 'INCONCLUSIVE' != 'FAIL' |
| 73 | C2 F2 T4-rest-unread needs both controls and all totals | `test_as_own_control_refused_is_inconclusive`: AssertionError: 'HOLDS (accepted, not applied)' != 'INCONCLUSIVE'; `test_a_missing_total_is_inconclusive`: AssertionError: 'HOLDS (accepted, not applied)' != 'INCONCLUSIVE'; `test_b_count_with_as_control_failed_is_inconclusive`: AssertionError: 'FAIL' != 'INCONCLUSIVE' |
| 74 | C2 F3 RT2/RT3 hold on attributable refusals only | `test_input_not_found_and_other_refusals_are_inconclusive`: AssertionError: 'HOLDS' != 'INCONCLUSIVE' |
| 75 | C2 F3 named events count only after an accepted request | `test_named_events_after_an_unattributable_refusal_are_inconclusive`: AssertionError: 'HOLDS' != 'INCONCLUSIVE' |
| 76 | C2 nit 4 only a rate limit is retried | `test_a_charge_signal_is_not_retried`: AssertionError: 3 != 1 : HTTP 402 |
| 77 | C2 nit 4 what counts as a rate limit | `test_charge_signals_are_not_rate_limits`: AssertionError: True is not false |
| 78 | C2 nit 4 flag on typed server calls | `test_rate_limits`: AssertionError: False is not true |
| 79 | C2 nit 4 flag on raw server calls | `test_the_result_check_flags_a_rate_limit`: AssertionError: False != True : 429 |
| 80 | C2 nit 4 flag on client requests | `test_flags`: AssertionError: False is not true |
| 81 | C2 nit 5 production phase needs an answer (feature-gated) | `test_feature_gated_case_without_a_production_answer_is_inconclusive`: AssertionError: 'HOLDS' != 'INCONCLUSIVE' |
| 82 | C2 nit 5 production phase needs an answer (S10) | `test_poll_vote_without_a_production_answer_is_inconclusive`: AssertionError: 'HOLDS' != 'INCONCLUSIVE' |
| 83 | C2 nit 6 exactly one request | `test_two_recorded_requests_have_no_answer`: AssertionError: 'permission' != 'no-response'; `test_generic_case_with_two_requests_is_inconclusive`: AssertionError: 'HOLDS' != 'INCONCLUSIVE' |
| 84 | C2 nit 6 G1's one POST /guest | `test_guest_attempt_with_another_request_has_no_answer`: AssertionError: 'HOLDS' != 'INCONCLUSIVE' |
| 85 | C2 nit 7 E5 with an unreadable stored user | `test_e5_is_inconclusive_when_as_stored_user_cannot_be_read`: AssertionError: 'HOLDS (accepted, not applied)' != 'INCONCLUSIVE' |
| 86 | C2 nit 7 S14 with an unreadable stored user | `test_s14_is_inconclusive_when_as_stored_user_cannot_be_read`: AssertionError: 'HOLDS (accepted, not applied)' != 'INCONCLUSIVE' |
| 87 | C2 nit 7 the stored user is matched by ID | `test_server_user_matches_the_id`: AssertionError: {'id': 'someone-else', 'role': 'admin'} is not None; `test_e5_is_inconclusive_when_as_stored_user_cannot_be_read`: AssertionError: RunStopped not raised |
| 88 | C2 nit 8 second Ctrl-C inside finish() | the test process stopped before reporting: KeyboardInterrupt |
| 89 | C2 nit 8 results written before the end of the run | `test_results_are_written_before_the_end_of_the_run`: StopIteration |
| 90 | C2 nit 9 accepted but unverified is not 'not restored' | `test_at_the_end_of_the_run`: AssertionError: Lists differ: [TemporaryChange(description="config_overr[1231 chars]e}})] != []; `test_during_a_case`: AssertionError: Lists differ: [TemporaryChange(description="config_overr[1231 chars]e}})] != [] |
| 91 | C2 nit 9 B's probe stopped by a guardrail leaves the removal unverified | `test_at_the_end_of_the_run`: AssertionError: Lists differ: [TemporaryChange(description="config_overr[1087 chars]e}})] != []; `test_during_a_case`: AssertionError: Lists differ: [TemporaryChange(description="config_overr[1087 chars]e}})] != [] |
| 92 | C2 nit 10 credential key names | `test_credential_keys_of_the_app_settings_model_are_redacted`: AssertionError: False is not true : firebase_server_key |
| 93 | C2 review: E5 keeps a stored-role FAIL before its restore | `test_e5_stored_role_fail_survives_a_rate_limited_restore`: AssertionError: 'INCONCLUSIVE' != 'FAIL' |
| 94 | C2 review: E5's failed restore stops the run | `test_e5_failed_restore_stops_the_run_after_its_row`: AssertionError: RunStopped not raised |
| 95 | C2 review: a failing progress write never replaces the stop | `test_a_failing_progress_write_never_replaces_a_guardrail_stop`: OSError: disk full; `test_ctrl_c_is_kept_when_the_progress_write_fails`: OSError: disk full |
| 96 | C2 review: a key still overridden keeps the change journalled | `test_a_key_still_overridden_keeps_the_change_journalled`: glow_stream_proof.usage.GuardrailStop: guardrail: api_calls would be passed; stopping befo… |
| 97 | C2 review: finish keeps its problems as it finds them | `test_finish_keeps_the_problems_found_before_a_second_ctrl_c`: AssertionError: False is not true |
| 98 | C2 review: results files are written atomically | `test_a_failed_write_leaves_the_previous_file_whole`: json.decoder.JSONDecodeError: Expecting value: line 1 column 1 (char 0) |
| 99 | C2 review: a Ctrl-C during the early write still reaches the restores | the test process stopped before reporting: KeyboardInterrupt |
| 100 | C3 RT2/RT3 a feature refusal is REFUSED (feature off), not HOLDS | `test_feature_refusals_are_refused_feature_not_holds`: AssertionError: 'HOLDS' != 'REFUSED (feature off; not a permission error)'; `test_rt2_feature_refusal_is_refused_feature_not_holds`: AssertionError: 'HOLDS' != 'REFUSED (feature off; not a permission error)' |
| 101 | C3 RT2 an auth or permission refusal without a positive control is INCONCLUSIVE | `test_rt2_auth_or_permission_refusal_has_no_positive_control`: AssertionError: 'HOLDS' != 'INCONCLUSIVE' |
| 102 | C3 RT3 an auth or permission refusal HOLDS only when B's own request succeeded | `test_rt3_refusal_without_a_successful_control_is_inconclusive`: AssertionError: 'HOLDS' != 'INCONCLUSIVE' |
| 103 | C3 RT3 the control, B's own identical request, is made | `test_rt3_auth_or_permission_refusal_holds_with_bs_own_request`: AssertionError: 'INCONCLUSIVE' != 'HOLDS' |
| 104 | C3 RT3 the matrix names B's session as RT3's control | `test_rt3_auth_or_permission_refusal_holds_with_bs_own_request`: AssertionError: 'INCONCLUSIVE' != 'HOLDS' |
| 105 | C3 RT3 the control's own events are not searched for the marker | `test_rt3_controls_own_events_are_not_searched`: AssertionError: 'FAIL' != 'HOLDS' |
| 106 | C3 F1 an observed FAIL survives a failed enabling request | `test_fail_survives_a_failed_enabling_request`: AssertionError: 'INCONCLUSIVE' != 'FAIL' |
| 107 | C3 F2 a restore's charge or limit signal is recorded | `test_a_signal_behind_another_stop_skips_the_cleanup`: AssertionError: Lists differ: ['/api/v2/chat/channels/delete', '/api/v2/users/delete'] != []; `test_a_signal_met_by_the_end_of_run_restore_skips_the_cleanup`: AssertionError: {'errors': [], 'channels_delete': 201, 'ch[407 chars]': 0} != {}; `test_rate_limited_restores_at_the_end_skip_the_cleanup`: AssertionError: {'errors': [], 'channels_delete': 201, 'ch[407 chars]': 0} != {} |
| 108 | C3 F2 finish() skips the cleanup after a recorded signal | `test_a_signal_behind_another_stop_skips_the_cleanup`: AssertionError: Lists differ: ['/api/v2/chat/channels/delete', '/api/v2/users/delete'] != []; `test_a_signal_met_by_the_end_of_run_restore_skips_the_cleanup`: AssertionError: {'errors': [], 'channels_delete': 201, 'ch[407 chars]': 0} != {}; `test_a_signal_as_the_runs_own_stop_skips_the_cleanup`: AssertionError: {'errors': [], 'channels_delete': 201, 'ch[407 chars]': 0} != {}; and 1 more |
| 109 | C3 F2 cmd_run adds its own stop to the run's record | `test_a_signal_as_the_runs_own_stop_skips_the_cleanup`: AssertionError: {'errors': [], 'channels_delete': 201, 'ch[407 chars]': 0} != {} |
| 110 | C3 F2 a signal met by the cleanup is recorded | `test_a_signal_met_during_cleanup_ends_it_and_is_recorded`: AssertionError: 0 != 1 |
| 111 | C3 F2 a signal ends the cleanup at once (untested until C3) | `test_a_signal_met_during_cleanup_ends_it_and_is_recorded`: AssertionError: 'users_delete' unexpectedly found in {'errors': ['channels: server POST /… |
| 112 | C3 F2 a signal met by the final configuration read is recorded | `test_a_signal_met_by_the_final_configuration_read_is_recorded`: AssertionError: 0 != 1 |
| 113 | C3 F2 a rate limit is a charge or limit signal | `test_a_signal_met_during_cleanup_ends_it_and_is_recorded`: AssertionError: 'users_delete' unexpectedly found in {'errors': ['channels: server POST /…; `test_rate_limited_restores_at_the_end_skip_the_cleanup`: AssertionError: {'errors': [], 'channels_delete': 201, 'ch[407 chars]': 0} != {} |
| 114 | C3 F2 the server's response hook marks and records a signal | `test_typed_and_raw_calls_mark_the_signal`: AssertionError: False is not true : 402 |
| 115 | C3 F2 the server's result check marks and records a signal | `test_the_result_check_marks_the_signal`: AssertionError: False is not true : 402 |
| 116 | C3 F2 a client's recorded request marks and records a signal | `test_every_client_signal_stops_at_once`: AssertionError: False is not true |
| 117 | C3 F2 a client's error marks and records a signal | `test_every_client_signal_stops_at_once`: AssertionError: False is not true |
| 118 | C3 review: the ledger records a signal as its stop is raised | `test_a_ctrl_c_that_replaces_the_stop_still_skips_the_cleanup`: AssertionError: Lists differ: [] != ['client A-role: HTTP 402; stopping at once']; `test_an_error_that_replaces_the_stop_still_stops_the_run`: AssertionError: RunStopped not raised; `test_a_signal_whose_stop_a_ctrl_c_replaced_skips_the_cleanup`: AssertionError: Lists differ: [] != ['client A-role: HTTP 402; stopping at once']; and 2 more |
| 119 | C3 review: a recorded signal stops the matrix after its case | `test_an_error_that_replaces_the_stop_still_stops_the_run`: AssertionError: RunStopped not raised |
| 120 | C3 nit 3 a pattern counts only at a line start | `test_a_pattern_matches_only_at_a_line_start`: AssertionError: Lists differ: [13] != []; `test_every_pattern_starts_a_line_once`: AssertionError: 2 != 1 : ('C2 nit 6 exactly one request', 'glow_stream_proof/proof_run.py') |
| 121 | C3 nit 3 an edited file that does not load is not demonstrated | `test_an_edit_that_does_not_compile_or_import_is_reported`: AssertionError: unexpectedly None : broken.py |
| 122 | C3 nit 4 a feature-on FAIL stays FAIL without a production answer | `test_feature_on_fail_survives_a_production_request_without_an_answer`: AssertionError: 'INCONCLUSIVE' != 'FAIL' |
| 123 | C3 nit 4 a polls-on FAIL stays FAIL without a production answer | `test_polls_on_fail_survives_a_production_vote_without_an_answer`: AssertionError: 'INCONCLUSIVE' != 'FAIL' |
| 124 | C3 nit 4 a guardrail met by the undo after an interruption stops the run | `test_a_guardrail_met_by_the_undo_after_an_interruption_stops_the_run`: AssertionError: GuardrailStop not raised |
| 125 | C3 nit 4 a second Ctrl-C keeps the problems finish() found | `test_second_ctrl_c_keeps_the_problems_finish_found`: AssertionError: 'temporary change not restored: still on' not found in ['the end of the run was… |
| 126 | C3 nit 4 a second Ctrl-C closes the client processes | `test_second_ctrl_c_closes_the_client_sessions`: AssertionError: {'A': <tests.fakes.FakeSession object …>} != {} |
| 127 | C3 nit 4 a client's error flags a rate limit | `test_the_error_only_check_flags_a_rate_limit`: AssertionError: False is not true |
| 128 | C3 nit 4 RT2/RT3 are INCONCLUSIVE unless B was listening | `test_a_refusal_while_b_is_not_listening_is_inconclusive`: AssertionError: 'HOLDS' != 'INCONCLUSIVE' |
| 129 | C3 nit 5 each request of a command is kept in the row | `test_each_request_of_a_command_is_kept_and_a_success_is_undone`: KeyError: 'requests' |
| 130 | C3 nit 5 a 2xx among a command's requests is undone | `test_each_request_of_a_command_is_kept_and_a_success_is_undone`: KeyError: 'client_success_undo' |
| 131 | C3 nit 6 B's probe stop is kept in the stops | `test_a_probe_stop_is_kept_and_its_signal_recorded`: AssertionError: "B's members query after AB's override removal: client B: HTTP 429; stopping at … |
| 132 | C3 nit 6 B's probe stop is recorded as a signal | `test_a_probe_stop_is_kept_and_its_signal_recorded`: AssertionError: Lists differ: [] != ['client B: HTTP 429; stopping at once'] |
| 133 | C3 nit 7 no unset of A's member field after a guardrail stop | `test_no_unset_after_a_guardrail_stop_in_bs_reads`: AssertionError: Lists differ: [('PATCH', '/channels/glow-match/p061i1-si[44 chars]']})] != []; `test_no_unset_after_a_guardrail_stop_in_the_control`: AssertionError: 2 != 1 |
| 134 | C3 nit 8 a failed read of A's stored user stops the run | `test_e5`: AssertionError: RunStopped not raised; `test_s14`: AssertionError: RunStopped not raised |
| 135 | C3 nit 8 a listing without A stops the run too | `test_e5_is_inconclusive_when_as_stored_user_cannot_be_read`: AssertionError: RunStopped not raised; `test_s14_is_inconclusive_when_as_stored_user_cannot_be_read`: AssertionError: RunStopped not raised |
| 136 | C3 nit 9 the usage ledger is written through a temporary file | `test_an_interrupted_save_leaves_the_previous_ledger_whole`: json.decoder.JSONDecodeError: Expecting value: line 1 column 1 (char 0) |
| 137 | C3 nit 10 the early-write failure note is redacted | `test_the_early_write_failure_note_is_redacted`: AssertionError: 'RuntimeError: refused near <redacted-jwt> and <redacted-secret>' not found in 'resu… |
| 138 | C3 nit 8 a guardrail stop on the read of A's stored user is not deferred | `test_a_guardrail_stop_on_the_read_is_the_runs_stop`: glow_stream_proof.proof_run.RunStopped: after E5: E5: A's stored user could not be read: Guardr… |
| 139 | C3 RT3 kept: both windows before the control | `test_rt3_marker_after_the_probe_survives_the_control_ending`: AssertionError: 'INCONCLUSIVE' != 'FAIL' |
| 140 | C3 F2 the client processes are closed when the cleanup is skipped | `test_a_signal_met_by_the_end_of_run_restore_skips_the_cleanup`: AssertionError: {'A': <tests.fakes.FakeSession object …>} != {}; `test_rate_limited_restores_at_the_end_skip_the_cleanup`: AssertionError: {'A': <tests.fakes.FakeSession object …>} != {}; `test_a_signal_as_the_runs_own_stop_skips_the_cleanup`: AssertionError: {'A': <tests.fakes.FakeSession object …>} != {} |
| 141 | C3 nit 5 each case's row lists only its own commands | `test_each_request_of_a_command_is_kept_and_a_success_is_undone`: AssertionError: Lists differ: ['cli[39 chars]s/{m_a} -> 201, POST /messages/{m_a} -… |
| 142 | C3 review: the production command's requests are listed in the row | `test_a_production_command_with_several_requests`: KeyError: 'requests' |
| 143 | C3 review: a 2xx among the production command's requests is undone | `test_a_production_command_with_several_requests`: AssertionError: 1 != 2 |
| 144 | C3 review: RT3's control counts only as the same request | `test_rt3_control_that_was_another_request_is_inconclusive`: AssertionError: 'HOLDS' != 'INCONCLUSIVE' |
| 145 | C3 review: S15 sends no unset after a recorded signal, whatever is in flight | `test_no_unset_after_a_signal_whose_stop_is_not_in_flight`: AssertionError: Lists differ: [('PATCH', '/channels/glow-match/p061i1-si[44 chars]']})] !… |
| 146 | C3 review: no undo after a recorded signal, whatever is in flight | `test_no_undo_after_a_signal_whose_stop_an_error_replaced`: AssertionError: 'made after the interruption: undo POST 201' != "not made: a charge or li… |
| 147 | C3 nit 5 a poll or group created among several requests is tracked | `test_a_poll_created_among_several_requests_is_deleted_at_cleanup`: AssertionError: 'client-poll' not found in [] |

### Decisions, deviations and limits

- **Decisions to confirm.**
  - **RT3's control is made only when A's request is refused with an authentication or permission error:** only then does the verdict need it. It is one more client request, B's `markRead`, and one more 2.5 s wait for B's events.
  - **RT3's control must match A's request by method and generic path** (the independent review, point 4). This can only turn a HOLDS into INCONCLUSIVE.
  - **Finding 2 goes beyond the suggested flag.**
    - A signal is recorded where it is met, in the ledger the server client and the client sessions share. The independent review showed that a flag set only where stops are caught misses a stop replaced in flight.
    - The run stops after a case whose error replaced a signal's stop.
    - The undo of a client success and S15's unset are not sent once a signal is recorded, whatever is in flight.
  - **A rate limit is a charge or limit signal,** as the README already said. A 429 at the end of the run is still retried, but the cleanup is skipped even if a retry succeeds.
  - **Nit 7:** the first suggested fix, skipping the unset, not the README-only option.
  - **Nit 8 extended to a 2xx listing without A:** it stops the run too, because A's stored role or profile is unknown either way.
  - **Nit 9:** the first suggested fix, the atomic write.
  - **Nit 5 in the procedures:** a 2xx among several requests is listed in the row but undone only in a generic case, where undo requests are defined. The procedures keep their own restores.
- **Deviations.**
  - Beyond the items: the independent review's points 1 to 4.
  - New files: `tests/test_stop_signals.py` and `tests/test_fix_reversals.py`.
  - `GuardrailStop` gained `at_once`, and `UsageLedger` gained `signals` and `stop_at_once`.
- **Limits.**
  - Nothing here was exercised live; the tests prove the harness's logic against fakes.
  - Under today's configuration RT2 cannot HOLD. A feature refusal is REFUSED (feature off), and an authentication or permission refusal has no positive control.
  - The production phase of a feature-gated generic case tracks no poll or user group it created, as before; no such case can create one.
  - `record_signal` at the run's catch sites now only adds stops that did not come through the ledger (the independent review, point 5).
  - `ledger.signals` is kept in memory. A later `cleanup` command does not see it; the operator reads the run's `stop_signals` and its "cleanup skipped" problem.
  - After a charge or limit signal the run still sends requests by design: the restores of journalled changes, with their verification, and the configuration re-read.
  - Existing behaviour, unchanged: T4-ws's HOLDS (accepted, not applied) does not consult its control.
- **No dependency change,** and nothing outside the owned paths.

### What P06.1-I2a must know

In addition to C1's and C2's lists above:

- **Rules that changed** (README "Verdict rules" states each):
  - **RT2 and RT3, feature refusal:** it is now REFUSED (feature off; not a permission error). Under today's configuration RT2's refusal (I1 recorded 400 code 18) therefore reads REFUSED (feature off), not HOLDS. I1's recorded result stays as recorded.
  - **Authentication or permission refusal:** for RT3 it HOLDS only when B's own identical `markRead` succeeded, with the same method and path. RT2 has no positive control, so it is INCONCLUSIVE.
  - A feature-gated case's observed FAIL stands when the enabling request fails.
  - E5 and S14 stop the run when A's stored user cannot be read.
  - S15 sends no unset of A's member field after a guardrail stop or a recorded signal.
- **Stop rules that changed:**
  - A charge or limit signal (HTTP 402 or 429, Stream code 9 or 99, charge wording) met anywhere in the run skips the cleanup. The run still restores and re-reads the configuration.
  - The problem "cleanup skipped: …" names the signal. Check it, then run `cleanup --apply`.
  - After a signal, no undo of a client success and no S15 unset is sent.
  - The run stops after a case in which an error replaced a signal's stop.
- **Outputs that changed:**
  - the results carry `stop_signals`;
  - rows may carry `requests` (a command that recorded more than one request), `control_event_types` (RT2 and RT3) and `member_field_unset` (S15);
  - the usage ledger is written through a `.partial` file;
  - the early-write failure note is redacted.
- **Not exercised live:** every fix above, including RT3's control against Stream's real `markRead` answers and a signal met at the end of the run.

### Manager verification of C3 (App Manager 3, 26 September 2026)

App Manager 3 checked the relayed report against the pushed branch. The manager makes no call to Stream, so nothing here was exercised live; the first live use is in I2a.

- **Identity:**
  - branch `claude/friendly-hypatia-ug6r52`, head `b40acd7f8c4198f8205040ca1bc3119addc6093a`, tree `d4391cb9fbddfb80094f464c093bb498643de147`; code head `a5e2221`;
  - it builds on the start `e5180ab` in two commits: 19 files, +2,723 and −175. The second commit changes only this record;
  - every path is owned, and all 52 files under `proofs/stream-chat/` have mode 100644. No dependency file, `.npmrc`, `pyproject.toml` or the committed baseline changed, and `git diff --check` is clean;
  - the six sections the C3 prompt protects are byte-identical to the start. The five in-place "(corrected in P06.1-C3)" markers are all in C2's own section.
- **Classification:** the trusted policy from `main` (`0f45e64`), run outside the tree with `python3 -I`, gave full scope (`behavior-or-empty`) for 19 paths, with one merge base.
- **Offline re-run,** in a scratch worktree at `b40acd7`, in clean processes without any `STREAM_*` variable. Installs got the proxy and CA variables by reference.
  - `pip install --require-hashes -r requirements-dev.lock`, then `pip check`: "No broken requirements found." `getstream` 6.1.0, Ruff 0.16.8, mypy 2.3.1.
  - `npm ci --ignore-scripts`: "found 0 vulnerabilities"; `stream-chat` 9.53.0.
  - Unit tests: `Ran 252 tests`, `OK`. Ruff check: "All checks passed!". Ruff format: "40 files already formatted". mypy: "Success: no issues found in 39 source files". `node --check` on both `.cjs` files: exit 0.
  - `checks/fix_reversals.py`: "reversals: 147, not demonstrated: 0", exit 0, in 13 minutes. The manager also read each reversal's failure reason, as AM3-18 requires: every failing test failed on an assertion or on the error its reverted fix causes, three reversals aborted through a Ctrl-C by design, and none failed through a syntax or import error. The checkout was unchanged afterwards.
- **Secret scan** of the whole diff (259,623 bytes): no JWT-shaped string, email address, private-key block, AWS-style or GitHub key, TLS-weakening setting, environment dump, secret assignment or the application's API key.
- **Code read,** at `b40acd7`. Each matches the report:
  - the signal record: `UsageLedger.stop_at_once` (`usage.py` around line 94) and its four raise sites in `server_api.py` and `client_bridge.py`; `stop_signals` (`proof_run.py` around line 369);
  - the matrix loop's stop after a recorded signal (around line 1117), `finish()`'s cleanup decision (around line 3028) and `cmd_run`'s use of the record (`cli.py` around line 178);
  - finding 1 (around line 1257), and the production phase's undo on any 2xx (around line 1253);
  - RT2 and RT3 (around lines 2615 to 2710): the kept row before the control, the control of the same request, its events kept apart, and the verdicts.
- **Integration:** merged into the manager branch as `8c1a8c08d77052a86cfc70fc38cb830eb641438a`, pushed alone at 16:15 UTC. Against its first parent, the merge brings exactly C3's 19 files; against C3's head it differs only in the manager's three records of `8881339`.
- **Hosted CI on `8c1a8c0`:** push run [36254790538](https://github.com/amthorn78/glow-dating-app/actions/runs/36254790538) and PR run [36254793755](https://github.com/amthorn78/glow-dating-app/actions/runs/36254793755) passed all six jobs, and the push run's gate says `Application checks passed`. The rendered suite passed 84 of 84 on the pinned Chromium in 3.8 minutes. No Foundation job runs the harness's own tests yet (I2b adds one); the offline re-run above covers them.

#### The decisions C3 left to the manager

All three are accepted:

- **RT3's control is sent only after an `auth` or `permission` refusal.** It costs one client request and one wait, and it is needed only when a refusal must be shown to be attributable.
- **A charge or limit signal is recorded where its stop is raised,** in the ledger the server client and every client session share, not only where stops are caught. That is stronger than the review asked, and it closes the Ctrl-C path C3's own review found.
- **E5 and S14 also stop the run when Stream's listing does not include A.** A was created by the run, so its absence means the run cannot know A's role or profile. Stopping is the conservative choice.

C3's limits stand as recorded. Its note that five older tests raise charge-like stops without the new flag goes to the review.

#### Disposition

- **C3 is verified and integrated.** "What P06.1-I2a must know" in C1's, C2's and C3's sections feeds I2a's prompt.
- **C3's exact-head review is next,** offline and scoped to C3's change, under the bound recorded in the disposition of the C2 review. I2a comes after it.

### Exact-head review of C3 (26 September 2026)

Nathan ran the review session at extra high, from revision 1 of the [review prompt](../../ephemeral/2026-09-26-p06-1-c3-review-prompt.md) (records commit `841fbad`), and relayed its report. The session committed and pushed nothing, and made no Stream call.

- **Verdict: approve.** The corrected harness is a sound base for I2a's live runs. The RT2 and RT3 change, the C2 review's findings 1 and 2 and nits 3 to 10, and C3's own four review points are confirmed fixed. The reviewer has no disagreement with the manager's decisions.
- **Six nits remain, and no blocking or should-fix finding.** Only nit 1 could create a false HOLDS, and only in principle; it is not new. The review also names one gap outside C3's change, for I2a's offline first step: a request a client session sends between commands is not checked for a charge or limit signal.

#### The report, as relayed

The session's notes before its report, verbatim:

> Confirmed `disconnectUser` only closes the WebSocket (no HTTP request). Checking reversal progress, then continuing through the procedures.
>
> Output is block-buffered to the log, so it will appear at the end. Continuing with S15, E5/S14 and RT2/RT3 code.
>
> Reviewed RT2/RT3 logic and the stored-user reads; now checking reversal progress and then the tests C3 added.
>
> Reading done for README changes. Checking S10's enabling path against the README's new "could not enable" sentence.
>
> Reversals at ~75/147. Reading C3's RT2/RT3 tests to design extra mutations that probe whether each fix's test would catch a different breakage.
>
> Reversal run still going. Meanwhile checking the records: the six protected sections against `e5180ab`, and C3's five in-place corrections.
>
> 103 of 147 reversals complete with no issues found so far. Meanwhile, I'm testing extra mutations in a scratch copy outside the repo to catch fixes whose tests might pass even if broken differently.
>
> Several "caught" results are only from the reversal-table pattern test (my edits touch lines the table quotes). Re-running with that test excluded to see which mutations real behaviour tests catch.
>
> The reversal run finished. Reading its full output and checking each failure reason.
>
> All 147 reversals check out, with C3's 48 failures matching expectations. I'll now write ad-hoc offline tests in scratch to confirm behavior on surviving mutations and check a RT3 window concern.
>
> Now the ad-hoc probes (scratch file outside the repo, no bytecode written):
>
> Probes confirm correct handling for the 402 cleanup case, the S15 budget stop, and RT3's control firing only after an auth refusal, with one probe showing a late A-attributed marker landing in RT3's unsearched window still holds. Now checking whether RT3's control (B's markRead) could affect later cases like T4-rest-unread.
>
> T4-rest-unread runs before RT3, so B's control `markRead` cannot affect it. Now the scope, mode, `diff --check` and secret-scan checks.
>
> Now the secret scan over the whole `git diff HEAD^1 HEAD`.
>
> Secret scan is clean (the 130 long strings are test names, two commit SHAs and a separator line). Now checking that C3's edits to existing C1/C2 tests did not weaken any assertion.
>
> Scope, modes, dependency files and the records' protected sections all check out. A few remaining README-vs-code checks (report rendering of `stop_signals`, S10 wording).
>
> The markdown report omits `stop_signals`—only the JSON includes it, with the "cleanup skipped" issue naming just the first printed signal. I'll now check C3's note on the five older tests that raise charge-like stops without the new flag.
>
> The five older tests' assertions don't depend on the new flag, though two raise a "429" stop without `rate_limited`, which production never actually produces—just a minor fidelity nit. Now confirming the checkout is still clean after all the runs.
>
> Checkout is clean (only ignored paths). Checking whether any other claim in C2's record section was false at C2's head but left uncorrected.
>
> Records corrections look complete. Spot-checking the line numbers C3's record cites at the code head.
>
> The per-reversal tally matches C3's record exactly (124 assertion, 20 error, 3 Ctrl-C by design). Next, I'll check whether a client success in both phases of a feature-gated case keeps both undo records in the row.
>
> All checks and probes are done; the checkout is untouched. Before writing the report, I'm loading Nathan's reporting skill, since it governs messages that report findings.

The report:

**Verdict: approve.** The corrected harness is a sound base for P06.1-I2a's live runs. There are no blocking or should-fix findings. Six nits remain, and none of them delays I2a under the manager's rule. Only nit 1 touches the three classes, and only in principle.

- **Prompt received:** revision 1, from commit `841fbad1be4d40b56af2aa801f613d76e687cc7e`.
- **Head reviewed:** `git rev-parse HEAD` printed `8c1a8c08d77052a86cfc70fc38cb830eb641438a`.
  - `HEAD^2` is `b40acd7f8c4198f8205040ca1bc3119addc6093a`. There is one merge base, `0f45e648099b415217938c25d7369164c0101def`, and the ancestor check printed "records build on the head".
  - `git diff --stat HEAD^1 HEAD`: 19 files, 2723 insertions, 175 deletions.
  - Under `proofs/`, the head is identical to C3's code head `a5e2221`.
- **Environment:** none of `DATABASE_URL`, `HD_API_KEY`, `GEO_API_KEY`, `STREAM_APP_ID`, `STREAM_API_KEY` or `STREAM_API_SECRET` is present. node v24.19.0, npm 11.9.0 and Python 3.12.14, all from `/root/.local/bin`.

**Classifications.** I used the trusted `main` policy (sha256 `dec69a26…`), extracted outside the tree and run with `python3 -I`.

| Run | Output |
|---|---|
| `main` → head | `{"full": true, "reason": "behavior-or-empty"}`, 111 paths |
| `63e922f` → head | `{"full": true, "reason": "behavior-or-empty"}`, 25 paths. The filter for non-Markdown files outside `proofs/stream-chat/` printed nothing |
| head → `841fbad` | `{"full": false, "reason": "ordinary-docs-only"}`, 5 paths |

##### Findings, most severe first

Paths are under `proofs/stream-chat/`.

**1. Nit. RT3's whole control window goes unsearched, not only B's own events.** `glow_stream_proof/proof_run.py:2651-2653`; README line 160.
- **Reproduced against the fakes:**
  - A's `markRead` got 403 / code 17.
  - An event from another user carrying A's marker arrived only in the window collected after B's control.
  - Result: HOLDS, with `marker_event_types: []` and `control_event_types: ["message.read"]`.
- **Why it is only a nit:**
  - It needs Stream to refuse A's request and still deliver A's marker more than about 5 s later.
  - At C2's head the same scenario was also HOLDS, because that window was never collected. So C3 adds no new path.
  - The README says only "B's own `message.read`" is set apart, which is more precise than the code.
- **Fix:** search the control window too. Leave out only B's own read events: type `message.read` or `notification.mark_read` whose `user.id` is B.
- **Classes:** it could create a false HOLDS in principle. It is not new, so as a nit it does not delay I2a.

**2. Nit (test gaps). Three C3 fixes still pass all tests when broken another way.** I ran each mutation against the full suite, with `tests/test_fix_reversals.py` removed, because that test fails on any edit to a line its table quotes. My probes confirmed that the head code behaves correctly in all three.
- (a) At `proof_run.py:2850`, changing `if exc.at_once:` to `if exc.rate_limited:` survives. Only a 429 met during cleanup is tested; a 402 is not. Fix: add a 402 or code-99 case to `SignalRecordTest.test_a_signal_met_during_cleanup_ends_it_and_is_recorded`.
- (b) At `proof_run.py:2180`, S15 still unsetting A's member field after a budget stop survives. The tests use only charge or rate-limit stops. Fix: add a budget-stop case to `MemberFieldUnsetTest`.
- (c) At `proof_run.py:2620`, sending RT3's control for every outcome survives. C3's decision to send it only after an `auth` or `permission` refusal is not tested. Fix: assert that B sent no `markRead` after a success, a feature refusal or an input refusal.
- **Classes:** none today. (a) protects the rule that no request follows a signal, so its test matters for regressions.

**3. Nit (README). The feature-gated rule names S10, but S10 does not follow it.** README line 150.
- The bullet covers S10's poll vote, but S10 has neither the "could not enable" rule nor the production-phase undo. `_poll_vote_phase` never judges the enabling request's status, and only `_generic_case` undoes.
- There is no verdict risk: S10 can HOLD only if the server's identical vote succeeds, which fails when polls did not turn on, and S10 never downgrades a FAIL.
- **Fix:** scope those two sentences to S2, S5, S6, S7 and S12.
- **Classes:** none.

**4. Nit. The production phase's undo note overwrites the feature-on phase's.** The note is set at `proof_run.py:1374`, called from `:1345` and then `:1271`.
- **Reproduced:** S5 with a 201 in both phases sent 3 undo DELETEs, but the row shows only "undo DELETE 200".
- A failed first undo still defers a stop, so nothing is hidden from the run's outcome.
- This behaviour dates from C2, and C3's any-2xx rule widens where it can occur.
- **Fix:** append the notes instead of replacing them.
- **Classes:** none.

**5. Nit, optional. The printed report does not show `stop_signals`.** `glow_stream_proof/report.py:82-89`
- Only the JSON results carry it. When cleanup was due, the "cleanup skipped: …" problem names the first signal.
- **Fix:** add a "Charge or limit signals" section to the report.
- **Classes:** none.

**6. Nit, optional. Older tests raise charge-like stops without the new flag.** This is the point the manager passed to this review.
- There are five: `tests/test_interruptions.py:280` and `:611`, and `tests/test_temporary_changes.py:114`, `:435` and `:513`.
- Two of them raise "HTTP 429" without `rate_limited=True`, which production never builds.
- None of their assertions depends on the flag, so I agree with C3 that they stay valid.
- **Fix:** build them through `ledger.stop_at_once`.
- **Classes:** none.

##### The C3 items and C3's own review points

| Item | Confirmed | Reason |
|---|---|---|
| RT2/RT3 change | Yes | A `feature` refusal gives REFUSED (feature off) at `:2673`. RT2's `auth` or `permission` refusal is INCONCLUSIVE, "no positive control". RT3 HOLDS only when B's own identical `markRead` succeeded with the same method and generic path (`:2690`), and the tests assert the same body. `input`, `not-found` and `other` stay INCONCLUSIVE. I1's recorded RT2 is unchanged. See nit 1 |
| F1: observed FAIL survives a failed enabling request | Yes | `:1257` |
| F2: signal met anywhere stops the cleanup | Yes | All four raise sites record the signal before raising (`server_api.py:107`, `:149`; `client_bridge.py:257`, `:264`). No production path builds a charge stop any other way. After a signal, the only requests are the journal's restores (with their re-read and B's probe) and the configuration re-read; client processes are only closed. `finish()` decides after its restores (`:3028`), and `cmd_run` no longer decides by itself |
| Nit 3: fix-reversal script | Yes | Patterns are anchored at line starts, and each edited file must compile and import. The F2 end-of-run reversal is repaired and fails with 0 != 4, 0 != 4 and the journal list, as the C2 review found |
| Nit 4: seven tests | Yes | Each has a test and a reversal that fails on an assertion |
| Nit 5: several requests per command | Yes | Both phases list every request; a 2xx is undone in generic cases. See nit 4 |
| Nit 6: B's probe stop | Yes | `:660-666` |
| Nit 7: S15's unset after a stop | Yes | The unset is not sent after a guardrail stop or once a signal is recorded. See nit 2(b) |
| Nit 8: unreadable stored user | Yes | Handled by `_stored_user` (`:2364`), at both of S14's read sites and at E5's |
| Nit 9: ledger written atomically | Yes | `usage.py:92` |
| Nit 10: early-write note redacted | Yes | `cli.py:200` |
| C3 review point 1 | Yes | A Ctrl-C or an error that replaces a signal's stop no longer loses it (ledger record, `:1117`) |
| C3 review point 2 | Yes | The production command's requests are listed and a 2xx is undone |
| C3 review point 3 | Yes | No undo (`:1405`) and no S15 unset (`:2184`) after a recorded signal |
| C3 review point 4 | Yes | The control counts only as the same request |

##### Areas reviewed with no findings

- **Focus 1, no request after a signal.** An exception, a second stop, a Ctrl-C or a failed write cannot lose the recorded signal. `cmd_run` and `finish()` both read it, and the run stops after the case. Nothing is sent after it except the journal's restores and the configuration re-read.
- **Focus 2, no silent pass.** C3 adds no HOLDS path without Stream's attributable refusal and a successful control of the same request. E5 and S14 with an unreadable user are INCONCLUSIVE and the run stops. RT3's control cannot affect T4-rest-unread, which runs earlier (phase 10, against RT3's phase 25).
- **Focus 3, observed FAILs.** No C3 change downgrades an observed FAIL. RT3's row kept before its control covers both windows.
- **Records.**
  - The five in-place corrections are accurate, marked, and all in C2's own section.
  - The six protected sections are byte-identical across `e5180ab`, the head and `841fbad`.
  - No recorded result changed.
  - Apart from nits 1 and 3, the README's rules match the code.
- **Scope.**
  - Only `proofs/stream-chat/**` (18 files) and the evidence record changed.
  - No dependency file, `.npmrc`, `pyproject.toml` or baseline changed.
  - All 52 files under `proofs/stream-chat/` are mode 100644, with no symlinks.
- **Credentials.**
  - The new outputs are generic or redacted: `requests`, `stop_signals` and the early-write note.
  - The allowlist, redaction and leak checks are unchanged.

##### Checks run

| Check | Result |
|---|---|
| `git diff --check HEAD^1 HEAD` | No output, exit 0 |
| Installs (`env -i`; proxy and CA variables by reference) | `pip check`: "No broken requirements found." getstream 6.1.0, Ruff 0.16.8, mypy 2.3.1. `npm ci`: "found 0 vulnerabilities". stream-chat 9.53.0, ws 8.21.3, https-proxy-agent 5.0.1 |
| Unit tests | `Ran 252 tests`, `OK` |
| Ruff check / Ruff format / mypy | "All checks passed!" / "40 files already formatted" / "Success: no issues found in 39 source files" |
| `node --check` on both `.cjs` files | Exit 0; exit 0 |
| `checks/fix_reversals.py` | "reversals: 147, not demonstrated: 0", exit 0, in about 11.5 minutes. By reversal: 124 failed on an assertion; 20 on the error their reverted fix causes (KeyError, RunStopped, JSONDecodeError and similar); 3 aborted on Ctrl-C by design. None failed through a syntax or import error. All 48 of C3's reversals fail for their stated reason, matching C3's table |
| Extra mutations (full suite) | 15 run; 3 C3-scope mutations survive (nit 2); the others were caught or were not real behaviour changes |
| Ad-hoc probes against the fakes | A 402 in cleanup ends it; a budget stop sends no S15 unset; RT3's control is not sent unless the refusal is `auth` or `permission`; nit 1 and nit 4 reproduced |
| Secret scan of the diff (259,623 bytes) | 0 JWT-shaped strings, emails, private-key blocks, AWS or GitHub keys, TLS-weakening settings, environment dumps or secret assignments. The 130 long strings are test names, two commit SHAs and a separator line |
| Protected sections (six) | Byte-identical |
| Repository state | `git status` is empty. Only ignored paths were created; no `.work/` |

##### Limits

- Nothing was run live. Whether B's `markRead` succeeds under the lockdown is for I2a to see; if it is refused, RT3 stays INCONCLUSIVE, which is conservative.
- I did not read hosted CI, and used no sub-agents.
- The secret scan could not look for the application's API key, because its variable is absent (OD-28).
- **Outside C3's change, for I2a's offline first step:** the runner clears its request records at each command (`client/runner.cjs:304`), and an SDK error it did not wait for is only noted (`proof_run.py:407`). So a charge signal on a request the SDK sends between commands would be neither checked nor recorded. With `recoverStateOnReconnect: false` such requests should be rare.
- I have no disagreement with the manager's decisions.
- I changed nothing in the repository, on GitHub or in Notion.

**NOTHING NEEDED.** Relay this to App Manager 3.

#### Manager verification of the review (App Manager 3, 26 September 2026)

The session committed nothing, so there is no branch to check. The manager checked the report's claims against the reviewed head.

- **Classification.** The manager's own runs, with the same trusted policy, gave full scope for 113 paths; full scope for 25 paths, with nothing outside `proofs/stream-chat/`; and `ordinary-docs-only` for 5 paths. The report counts 111 paths for the first run; the classifier lists 113. The result, full scope, is the same.
- **Findings, at `8c1a8c0`:**
  - **Nit 1:** the control's events are collected apart (`proof_run.py:2651`), and the marker is searched only in the windows after A's request and after the probe (`:2652`). So nothing in the control window is searched, not only B's own read.
  - **Nit 2:** the cleanup test's signal is a 429 (`tests/test_stop_signals.py:98-116`); `MemberFieldUnsetTest` (`:241`) stops only on a charge or rate-limit signal; and the one RT3 `markRead` assertion compares B's control with A's request after a refusal (`tests/test_answers.py:303`).
  - **Nit 3:** `_poll_vote_phase` reports the enabling request's status but never judges it (`proof_run.py:2072` onward).
  - **Nit 4:** `_undo_client_success` assigns the row's `client_success_undo` (`proof_run.py:1374`), so the production phase's call (`:1271`) replaces the feature-on phase's (`:1345`).
  - **Nit 5:** the printed report lists the notes, the stops, the changes not restored and the problems after the run, not `stop_signals` (`report.py:80-90`).
  - **Nit 6:** the five stops are plain `GuardrailStop`s, two of them "HTTP 429".
  - **The gap under "Limits":** the runner starts each command with `records = []` (`client/runner.cjs:304`), so a request the SDK sends between commands is never reported, and `_send` only notes asynchronous errors (`proof_run.py:403-407`).
- **Hosted CI on the records commit `841fbad`:** push run [36255249228](https://github.com/amthorn78/glow-dating-app/actions/runs/36255249228) classified it as ordinary documentation, and its gate passed; PR run [36255252552](https://github.com/amthorn78/glow-dating-app/actions/runs/36255252552) passed all six jobs.
- **Not re-run by the manager:** the session's installs, tests, reversal run, 15 mutations and probes. Its installs, tests and reversal summary match the manager's own run on C3's head.

#### Disposition

- **C3's code head `8c1a8c0` is approved.** No finding is blocking or should-fix, so under the bound in the C2 review's disposition nothing delays I2a.
- **I2a's offline first step, before any live call,** takes the six nits and the gap:
  - **required:** nit 1, the one finding that could create a false HOLDS, however unlikely; the gap, so that every request a client session sends, between commands too, and every asynchronous SDK error are checked for a charge or limit signal, which Nathan's $0 budget depends on (OD-12); and nit 2(a), the test of the rule that no request follows a signal;
  - **fixed, or left with a one-line reason:** nits 2(b), 2(c), 3, 4, 5 and 6.

  Each code fix gets a test that fails without it and a reversal in `checks/fix_reversals.py`. I2a's exact-head review covers them with the rest of I2a.
- **I2a's prompt is next.** It authorizes credential use and live provider actions, so the Dev Manager reads it before Nathan runs it (DM-04).
- **Added after DM-04** (26 September): before its first live call, I2a also adds a guard in code for destructive calls, closing checks that see application-wide settings and DM-04's finding 9(c), and makes an independent review pass over its new code. Revision 2 of its prompt carries them; see the review log, "DM-04".

## P06.1-I2a

The first slice of I2a: revocation and safety. Step 1 fixed the C3 review's items, the guard (DM-04 finding 1) and the closing checks (DM-04 finding 2) offline, in a commit of its own, before any Stream call. Step 2 added the I2a cases and their verdict rules offline. An independent check then read the whole change before the first live call, and its findings were fixed. The live runs used application 1729640 only, from committed and pushed heads at which the offline checks and every fix reversal passed.

- **Prompt:** revision 2, from commit `6e67fd680e97db046290dcaa14331085f0560dfd` (`docs/ephemeral/2026-09-26-p06-1-i2a-implementation-prompt.md`).
- **Branch:** `claude/p06-1-i2a-revocation-safety-wms9ea`. **Start:** `6e67fd680e97db046290dcaa14331085f0560dfd`.
- **Step 1 commit:** `f3ef40b837253a6eedfd7ae12c11bda8172cc135`.
- **Code head:** `7ce93cc6ea7d197a5d952f55ea414ff41cdcd581`, the head of the reserve rerun (run 2). Run 1 ran from `5df522cf2edd3fad8275898e363ce23490109de1`. Every check below ran on the code head. The commit that adds this section changes only this record; it was not exercised live.
- **Date:** 26 September 2026.

### Environment

| Check | Result |
|---|---|
| `DATABASE_URL`, `HD_API_KEY`, `GEO_API_KEY` | None present (names only were checked; the launcher also refuses to start if one is present) |
| `STREAM_APP_ID`, `STREAM_API_KEY`, `STREAM_API_SECRET` | Present (names only). They reached the server process through its environment only, by an allowlisting launcher that puts no value on a command line, in a file or in any output; offline checks ran in `env -i` processes without them |
| Versions | node v24.19.0; npm 11.9.0; Python 3.12.14 |

The environment was never dumped. There were no connections to a database, HDE, Railway or any provider other than Stream; on Stream, only application 1729640. No `playwright install`, `eas` or `migrate`; no `configure --apply` or `restore --apply`; no change outside application 1729640, to the plan, billing, Maker, the team, the keys or the region; no webhook, hook or push; no real people or personal data. Besides Stream's API, the only outbound requests were the package installs (PyPI and the npm registry, through the proxy, with the proxy and CA variables passed by reference), Stream's documentation pages (getstream.io) and GitHub pushes of this branch.

### Step 1: the C3 review's items, the guard and the closing checks

Commit `f3ef40b837253a6eedfd7ae12c11bda8172cc135`, on its own, before any step 2 change. No Stream call was made before it. Paths are under `proofs/stream-chat/`; line numbers are at the code head. Each test named fails with its fix reverted and passes with it (see "Checks", item 5).

| Item | What was done, and where | Tests |
|---|---|---|
| Nit 1 (required). RT3's whole control window went unsearched | Fixed with the suggested fix. The control window is searched for the marker too, leaving out only the control member's own read events: type `message.read` or `notification.mark_read` whose `user.id` is B (`_searched_control_events`, `proof_run.py:2990`; used at `:2908`). README "Verdict rules", the RT2 and RT3 bullet, says so | `tests/test_answers.py` `PayloadRefusalAttributionTest.test_rt3_control_window_is_searched_but_for_bs_own_read_events` |
| The gap (required). A request the SDK sends between commands, and an asynchronous SDK error, were neither checked nor recorded | Fixed. **The runner** keeps every request a command did not finish and every one the SDK sends between commands (`client/request-log.cjs`; `RequestLog`), and reports them in the next reply or in its exit reply (`background_requests`, `background_api_calls`), with a rate limit's own `x-ratelimit-*` headers and no other header. Asynchronous errors carry Stream's status and code (`client/runner.cjs`, `asyncError`). **The harness** checks each for a charge or limit signal like any client request, records it in the ledger and stops at once (`client_bridge.py`, `_late_signals`, `:368`; `_late_signal` at step 1, renamed when the independent review's point 3 made it record every signal); calls sent between commands are counted. **As a session closes**, its exit reply is read and checked too (`_exit_signal`, `:432`); the signal is recorded always and raised only when nothing else is in flight (`:429`). **The end of the run** closes the sessions before it decides the cleanup (`proof_run.py:3349`), so a signal a closing session reports skips it | `tests/test_client_session.py` `LateRequestsTest` (four tests) and `ClosingSignalTest` (three); `tests/test_runner.py` `RequestLogTest` (two) and `RunnerReportsTest`; `tests/test_stop_signals.py` `ClosingSessionSignalTest` (two) |
| Nit 2(a) (required). A 402 or code 99 met during the cleanup | Test added: a 402 met by the channel delete ends the cleanup; the user delete is never sent (`proof_run.py:3140`) | `tests/test_stop_signals.py` `SignalRecordTest.test_a_charge_signal_met_during_cleanup_ends_it_too` |
| Nit 2(b). S15's unset after a budget stop | Test added | `tests/test_stop_signals.py` `MemberFieldUnsetTest.test_no_unset_after_a_budget_stop_in_bs_reads` |
| Nit 2(c). RT3's control only after an authentication or permission refusal | Test added: B sends no `markRead` after a success, a feature refusal or an input refusal | `tests/test_answers.py` `PayloadRefusalAttributionTest.test_rt3_control_is_sent_only_after_an_auth_or_permission_refusal` |
| Nit 3. The README's feature-gated rule named S10 | Fixed: the two sentences name S2, S5, S6, S7 and S12, and a sentence says what S10 does instead (README "Verdict rules") | — (README) |
| Nit 4. The production phase's undo note overwrote the feature-on phase's | Fixed: the notes are appended, the second labelled `production:` (`_undo_client_success`, `proof_run.py:1542`) | `tests/test_answers.py` `ProductionPhaseAnswerTest.test_both_phases_undo_notes_are_kept` |
| Nit 5. The printed report did not show `stop_signals` | Fixed: a "Charge or limit signals" section (`report.py:86`) | `tests/test_usage_and_report.py` `ReportTest.test_the_report_lists_every_charge_or_limit_signal` |
| Nit 6. Older tests raised charge-like stops without the flag | Fixed: the five stops are built through `ledger.stop_at_once` | The five tests, unchanged in what they assert |
| DM-04 9(c). The cleanup's prefix scan left out deactivated users | Fixed: `include_deactivated_users` in `_delete_users` (`proof_run.py:3190`) and in the artifact scan | `tests/test_cleanup.py` `GuardedCleanupTest.test_a_deactivated_user_with_the_prefix_is_found_and_deleted` |
| The guard (DM-04 finding 1) | Fixed. One guard (`guard.py`, `refusal`, `:254`) runs in the server client's request hook, before a request is counted or sent (`server_api.py`, `_before_request`, `:127`), so typed SDK calls pass it too. During a run the run is its scope (`proof_run.py:402`); `cleanup --apply` is scoped to the proof's prefix (`cli.py:273`). It refuses a change that names a user or channel the run did not create, any `PATCH /api/v2/app` other than a journalled temporary setting, a channel-type change other than a journalled `glow-match` toggle, a delete of a message the run did not record, a change to a poll or group it did not record, and any other kind of change the proof does not make. A refusal names the request's shape, never an identifier, and stops the run after the case's row | `tests/test_guard.py` (15 tests, with the real `ServerApi` on an `httpx.MockTransport` for the hook) |
| The closing checks (DM-04 finding 2) | Fixed. `configuration.verify` compares every application setting the committed baseline records with its recorded value, except guest creation (`recorded_differences`, `configuration.py:245`), so preflight, the end of the run and the dry-run `configure` see an application-wide `revoke_tokens_issued_before`, `webhook_url`, `event_hooks`, `custom_action_handler_url` or a `before_message_send_hook_url` (absent in the baseline, so it must stay absent or empty) | `tests/test_configuration.py` `RecordedSettingsTest` (five tests); `tests/test_closing_checks.py` (three) |
| Signals by kind (DM-04 finding 4) | Fixed. A stop records whether its wording mentions billing (`usage.py`, `mentions_billing`, `:209`), and `only_rate_limit` (`:69`); the "cleanup skipped" problem says what to do by kind (`proof_run.py`, `signal_instruction`, `:454`), and a rate limit's stop names its reset. README "Budget guardrails", "Signals, by kind" | `tests/test_stop_signals.py` `SignalKindTest` (three tests), `tests/test_server_api.py` `SignalKindAtTheServerTest`, `tests/test_client_session.py` `ClientSignalKindTest` |

### Step 2: the I2a cases and their verdict rules

The rules were written, committed and pushed before any live run of these cases; the README section "P06.1-I2a cases" (under "Verdict rules") is their full statement, and the module docstrings of `glow_stream_proof/mechanisms.py` and `glow_stream_proof/i2a.py` repeat them. In short:

- **The mechanisms** (`RV-remove`, `RV-ban`, `RV-hide`, `RV-freeze`, `RV-revoke`, `SD-deactivate`, `SD-delete`), one case each, on a channel of its own, applied server-side through the guard. For each member, before and after, by the same member: `rest` (a REST read of the channel), `ws` (whether the already-open subscription receives a server channel update and M2's message), `token_reuse` (a new session with the member's existing token connects and reads), `s15` (the member's own member write), and for the account-level mechanisms `token_issued_after`. A dimension is `ended` only on Stream's authentication or permission error after the same request by the same member succeeded before (the matrix quality rule); the subscription is `ended` only when a listener received the probe and the member did not, in two windows, with no connection change that could explain it. **MEETS the history policy** only when every dimension is `ended` for the member acted on (both members for the freeze), its own client cannot undo it (the server's replay is the control) and the channel's first message is retained; **DOES NOT MEET** when a dimension is `not ended`, the client undid it or the messages are gone; INCONCLUSIVE otherwise.
- **Recorded for each mechanism**, not judged: the event types each member receives, system messages, where M2 (the acting user, named for the removal, the ban and the freeze) appears, the app send path's refusal without a Stream call (check `AP12-<mechanism>`, judged), and Stream's answer to a server-side send on the affected member's behalf (an observation only: server-side calls bypass Stream's permission checks).
- **Tokens and devices:** R has two devices; `revoke_tokens_issued_before` is per user; a token issued at once after it has a back-dated `iat` and is refused by design; one issued 7 s later is `token_issued_after`. TD-expiry: a second device of A with a 25 s token, before and after its expiry.
- **OUT-send**: the outage is injected in-process only (an `httpx` transport that raises `ConnectError`); no real outage is claimed.
- **S15-map** (RECORDED, a mapping) and **F9-pin/F9-archive**, **F9-invite-accept/-reject**, the finding-9 reads and generic cases, and the **existence oracle** (`EO-channel`, `EO-user`, `EO-message`).
- **G2 and S10** have new setups: G2's guest is created server-side and connects by ID; S10's poll message goes to a channel of its own, created while polls are on.
- **The history policy is Nathan's OD-12**; whether a mechanism meets it when applied to both members is derived from the member it is applied to (by symmetry); only the freeze is judged for both.
- **Interpretation to flag** (the prompt's section 8): the four channel-level mechanisms share the synthetic users M1 and M2, each on a separate channel of its own, following revision 1 of the I2a prompt ("Channel-scoped mechanisms can share users on separate channels; user-scoped ones ... need their own users") and DM-04 finding 5's count basis. Each family's controls, made before its mechanism, show that no earlier family reached its channel.

### Stream behaviour, from Stream's documentation

Read on 26 September 2026 by two read-only research sub-agents, which fetched only getstream.io pages and made no Stream call. Each quotation that a design choice rests on was re-checked verbatim. "Not documented" means not found on the pages listed.

| Topic | What the documentation says | Used for |
|---|---|---|
| Member removal | `removeMembers` removes users; an optional message object makes client SDKs show a system message; no automatic system message. Events: `member.removed` to watchers, `notification.removed_from_channel` to the removed user's other clients. Whether a removed watcher keeps receiving events, and whether member custom data survives removal: not documented | RV-remove; the S15 mapping's removal question |
| Channel ban | `channel_cid` makes a ban channel-scoped ("the user will still be able to use the rest of the app"); `banned_by_id` is optional; banned users "cannot post". Reading, events and own-membership writes of a banned member: not documented. `user.banned` goes to the banned user's clients; the webhook form carries `created_by` | RV-ban; naming M2 as `banned_by_id` |
| Token revocation | `revoke_tokens_issued_before` on the user (a partial update), reversible with null; tokens with `iat` before it fail; tokens without `iat` are invalid. Effect on an open WebSocket: not documented | RV-revoke; the `iat` record |
| Hide | Removes the channel from query channels "until a new message is added"; only members can hide; `channel.show()` from the client undoes it; `channel.hidden` and `channel.visible` go to the user's clients. Reading a hidden channel by ID: not documented | RV-hide; hiding again before the member's own `show` |
| Freeze | Prevents new messages and reactions; reading stays allowed; `UpdateChannelFrozen` and `UseFrozenChannel` permissions; server-side calls are not permission-checked | RV-freeze |
| Deactivation | The user "will not be allowed to perform API requests / connect"; data retained; reversible; `mark_messages_deleted` soft-deletes messages. The documentation does not use "suspend" | SD-deactivate, as Stream's suspension mechanism |
| Hard delete | With `user: hard`, `messages` and `conversations` must also be `hard` (omitted means promoted; `conversations: soft` is an error); a conversation is a channel of two or fewer members that includes the user. Asynchronous, with a task | SD-delete's options; cleanup's handling of a channel the delete removes |
| Token expiry | Code 40 is "token expired"; with a static token "the connection fails once that token expires"; whether the server closes an open WebSocket at expiry: not documented | TD-expiry |
| System messages | Created only on request (a message object on member changes or a channel update, or a `system` message) | The system-message record of each mechanism |
| Custom and AI events | `ai_indicator.*` are custom events; custom events need the `custom_events` feature and the `SendCustomEvent` permission | F9-ai, feature-gated like S12 |
| Member partial update | "Only custom data and channel roles are eligible for modification"; pinned and archived use the same update | The S15 mapping; F9-pin and F9-archive |
| Invites | `acceptInvite` may carry a message that posts a system message; a message on reject is not documented | F9-invite-accept and F9-invite-reject |
| Leaving | Needs the `Leave Own Channel` permission | F9-leave |
| Reads | `queryReactions` needs read permission client-side; `queryMessageHistory` is server-side only and Enterprise only; `sync`: not documented | The finding-9 reads |
| Get Channel | `GET /channels/{type}/{id}`: 404 when the channel does not exist, 403 without `ReadChannel` ("a 404 is the expected negative answer") | EO-channel's GET probe |
| Guests | Server-side `createGuest` returns `user` and `access_token`; whether `guest_user_creation_disabled` also blocks server-side creation: not documented | G2's new setup |
| Polls | No channel-level override for polls; propagation of a type change: not documented | S10's new setup |
| Error codes | 4 input, 5 authentication, 9 rate limit, 16 does not exist, 17 not allowed, 18 event not supported, 19 feature disabled, 40 token expired, 43 signature invalid, 70 no access to channels, 99 app suspended | The classification the matrix already uses |

Pages relied on (Markdown forms of the pages at the same paths): chat/docs/javascript: channel-members, event-object, creating-channels, query-channels, query-members, channel-update, channel-management, hiding-channels, freezing-channels, disabling-channels, permissions-reference, moderation, silent-messages, send-message, tokens-and-authentication, channel-features, pinning-channels, archiving-channels, channel-invites, threads, send-reaction, pending-messages, polls-api, authless-users; chat/docs/python: channel-members, event-object, webhook-events, hiding-channels, freezing-channels, chat-permission-policies, moderation, silent-messages, ai-message-streaming, audit-logs, get-channel, channel-invites, archiving-channels; chat/docs/node: channel-members, channel-features, channel-level-settings, chat-permission-policies, webhook-events, ai-message-streaming, get-channel, channel-invites; chat/docs/go-golang/pinning-channels; chat/docs/dotnet-csharp: channel-members, channel-invites; moderation/docs/node and python: content-moderation/flag-mute-ban, integrations/stream-chat; docs/platform: authentication, users, gdpr, async-operations, permissions, webhooks, api-error-codes, backend-sdks; and the legacy chat/docs/sdk/android/v5/client/moderation-tools (marked "no longer actively maintained"). The REST reference at getstream.github.io/protocol was not read.

The installed SDK sources were read for every request shape: stream-chat 9.53.0 (`dist/cjs/index.node.js`: `hide`, `show`, `banUser`, `unbanUser`, `shadowBan`, `acceptInvite`, `rejectInvite`, `addMembers`, `removeMembers`, `pin`, `archive`, `updateAIState`, `partialUpdateMember`, `updateMemberPartial`, `getReplies`, `getReactions`, `getMessagesById`, `queryReactions`, `getThread` (which watches by default), `queryMessageHistory`, `sync`), and getstream 6.1.0 (`create_token` sets `iat` to now minus 5 s; typed calls wrap `httpx.RequestError` in `StreamTransportException`; the request models for update channel, ban, deactivate, delete users, member partial update, hide and create guest).

### The independent check before the first live call

A fresh reader (a read-only sub-agent of this session, given no conclusions of mine) reviewed the complete step 1 and step 2 change at `5b2403d` before any live call: the guard, the stop paths, the cleanup of every new state and the verdict rules. It made no change, no network or live call, and read no environment value. It ran the unit tests (359, OK), `ruff`, `mypy`, `node --check` and `checks/run_plan.py` (fits) in clean processes, and wrote offline probes against the fakes. It found 2 blocking findings, 7 more to fix before the live run, and 7 nits; it found no gap in the guard. Every finding was fixed before the first live call, each with a test that fails when the fix is reverted (`checks/fix_reversals.py`, entries named "I2a review …"). Paths are under `proofs/stream-chat/`; line numbers are at `7ce93cc`.

| # | Finding | Fix | Where | Tests |
|---|---|---|---|---|
| 1 (blocking) | The S15 mapping's restore could be skipped: a field was put back only when a re-read showed the change, outside any `try/finally`, so a write the server's control applied, or one interrupted (B's session ending), was left in place (A left `channel_moderator` or banned in AB) and the run went on. F9-pin and F9-archive had the same gap | A's member record is read before anything is written (nothing is written if it cannot be read). Every write that may have changed it is put back when its field ends, however it ends (`restoring_member`), and the whole record is read again and compared with the original in every mapped field (`restore_member`); a record that cannot be read or does not match stops the run after the case. Nothing is sent after a guardrail stop or a recorded signal. A field that already reads as it was is not written again, so a write Stream accepted but ignored needs no restore it might refuse (found in this session's own pass over the fix) | `i2a.py` `restoring_member` :411, `restore_member` :477, `_map_field` :540, `own_member_flag` :683 | `tests/test_i2a.py` `S15MapTest` (seven tests), `OwnMemberFlagTest` (nine) |
| 2 (blocking) | The subscription dimension could be `ended` falsely: the member judged was collected first with a 2.5 s wait and the listener after it, so a late delivery to the member counted as a miss; a dropped or recovered connection was ignored | The listeners are collected first and the judged members last; a member that missed the probe while another session received it is collected a second time; a `connection.changed` or `connection.recovered` in the member's windows after the mechanism makes a miss `not shown` (any close or recovery for a channel-level mechanism; a recovery for an account-level one, where a close may be the mechanism itself, and the row says so) | `mechanisms.py` `probes` :511, `window_order` :581, `unattributable` :596, `ws_dimension` :154 | `tests/test_mechanisms.py` `WindowTest` (five), `RulesTest.test_the_subscription_ends_only_with_a_listener_that_received_it` |
| 3 | Only the first charge or limit signal in a client reply was recorded, so a 402 behind a 429 could be reported as "only a rate limit"; the calls were counted before the checks, so the budget could raise first | Every signal in a reply (its requests, the command's error, requests sent between commands, asynchronous errors) is recorded before anything raises; the reply's calls are counted after the checks, without a check that could raise over a signal | `client_bridge.py` `send` :260, `_reply_signals` :331, `_late_signals` :368 | `tests/test_client_session.py` `EverySignalTest` (two) |
| 4 | RV-revoke could MEET the policy while a token issued after the revocation still read the conversation | A dimension `token_issued_after` for the account-level mechanisms: the revocation's token issued past the `iat` back-dating, and for deactivation and deletion a token issued at once. It is required for MEETS | `mechanisms.py` `ACCOUNT_DIMENSIONS` :87, `fresh_token` :1060, `judge_dimensions` :1075, `policy_verdict` :231 | `FamiliesTest.test_token_revocation_on_two_devices`, `test_deactivation_and_the_hard_delete`, `test_the_policy_requires_every_dimension_of_the_mechanism` |
| 5 | F9-pin and F9-archive could HOLD with no positive control for B's read (B's query refused, or without A's member entry), or HOLD "accepted, not applied" from a failed read | HOLDS (filtered) only with a 2xx server read showing the flag and B's 2xx read returning A's member record without it; HOLDS (accepted, not applied) only from a 2xx read of A's record; INCONCLUSIVE otherwise | `i2a.py` `own_member_flag` :683 | `OwnMemberFlagTest` |
| 6 | The existence oracle held on identical non-attributable answers (two 500s, two 400s) | Each pair is judged: not attributable (no answer, a local error, an unclassified status) is INCONCLUSIVE; different is FAIL; identical is HOLDS only for authentication or permission refusals, 404s or successes; identical input or feature errors are INCONCLUSIVE | `i2a.py` `pair_verdict` :903, `oracle` :920 | `OracleTest` (eight) |
| 7 | An interruption could lose an observed FAIL or a family's evidence: EO and F9-pin/archive kept no partial row; a family's `events()` and `reuse()` raised for a member whose session had ended; a family's DOES NOT MEET became INCONCLUSIVE if a session's close raised afterwards | The oracle keeps its row after each pair, pin and archive after the leak check and after the restore, the S15 mapping after each field; a family judges and keeps its row after each step (its DOES NOT MEET is kept as a FAIL is: `matrix.KEPT_WHEN_INTERRUPTED`); an ended session's remaining dimensions are `not shown`, naming the end, and the family goes on | `mechanisms.py` `step` :1134, `events` :458, `collect_after` :904, `reuse` :988; `proof_run.py` `_interrupted_row` :642; `matrix.py` :219 | `StopsTest.test_an_ended_client_session_ends_only_its_case`, `StopsTest.test_an_interrupted_family_keeps_what_does_not_meet_the_policy`, `StopsTest.test_a_rate_limit_in_a_probe_keeps_what_was_observed`, `OracleTest.test_an_oracle_seen_before_an_interruption_stays_a_fail`, `S15MapTest.test_a_field_the_control_set_is_restored_when_bs_session_ends`, `OwnMemberFlagTest.test_a_leak_stays_a_fail_when_the_control_is_interrupted` |
| 8 | SD-delete's channel was recorded as possibly gone only after the task wait, so a run stopped during the wait named it in the cleanup's batch | Recorded before the delete is sent | `mechanisms.py` `apply` :816 | `FamiliesTest.test_a_stop_during_the_hard_deletes_task_leaves_the_channel_checked_first` |
| 9 | After a rate limit the reserve rerun was not actually available: `cleanup --apply` does not delete a `deleted-user-1729640-…` user, and preflight refuses a run while one exists | README amended, as the prompt requires the user to be reported and left: then no further run can start, the reserve is not available, and live work ends | README "Signals, by kind" | — (README) |
| Nit | The hide's undo was judged even when the server's re-hide failed | The member's `show` is sent only once the channel is hidden again (2xx and not listed); otherwise the undo is INCONCLUSIVE | `mechanisms.py` `undo` :1235 | `FamiliesTest.test_a_hide_that_is_not_made_again_leaves_the_undo_unjudged` |
| Nit | A hard delete whose task did not complete was judged as applied | The family is INCONCLUSIVE whatever it observed | `mechanisms.py` `unjudgeable` :1125 | `FamiliesTest.test_the_cleanup_names_no_user_or_channel_that_is_gone` |
| Nit | A connect as H after the delete may create H again | Recorded (`connected_after_the_delete`), and H is named at cleanup again | `mechanisms.py` `reuse` :988 | `FamiliesTest.test_a_connect_that_creates_the_deleted_user_again_is_cleaned_up` |
| Nit | The run plan ignored the session's counts in `.work/usage-ledger.json` | Added, read only (`session_used_before`) | `checks/run_plan.py` `session_used` :69 | `tests/test_run_plan.py` `test_what_the_session_already_used_is_counted` |
| Nit | The guard did not check a poll update's poll in its body (`PUT /api/v2/polls`), nor a mute's `target_id` | Both checked | `guard.py` :313 and `USER_ID_KEYS` :52 | `tests/test_guard.py` `RefusalTest` |
| Nit | Stale S10 text ("created in AB") | Names S10's channel | `proof_run.py` :2235 | — |
| Nit | A 401 code 40 from a member's own 900 s token expiring naturally would count as `ended` | A family runs only while M1's and M2's tokens have at least 300 s left; a dimension is `ended` only while the member's own token had at least 60 s left at the end of the observations (each token's seconds left are recorded); a case before the families runs only while A's, B's, X's and D's tokens have at least 120 s left, and AP11 is not made otherwise | `mechanisms.py` `execute` :660, `judge_dimensions` :1075; `proof_run.py` `_setup_tokens_expiring` :1100, `run_matrix` :1210 | `tests/test_mechanisms.py` `TokenLifetimeTest` (three) |

Two further changes came from this session's own pass over the fixes: TD-expiry's controls count only when they finished at least 3 s before the token's `exp`, and a token without `exp` is INCONCLUSIVE (`i2a.py` `token_expiry` :133; `TokenExpiryTest`); G2's server-side guest creation is tried again with guest creation enabled after any refusal, not only a 403, because Stream does not document the status (`i2a.py` `g2_session` :1085; `G2SetupTest.test_any_refusal_is_tried_again_with_guest_creation_enabled`). The fake server now issues tokens as `getstream`'s `create_token` does (`iat` back-dated 5 s, `exp` from now), so the fakes exercise the token-lifetime rules.

### The run plan's count

Counted offline before any live call (`checks/run_plan.py`, the complete set and each case family on its own against the fakes, through the same usage ledger), and again at `7ce93cc` with the same result:

| | Users | Channels | Peak connections | API calls (fakes) |
|---|---|---|---|---|
| The complete set (114 cases) | 11 | 18 | 6 | 605 |
| The base setup | 4 | 2 | 3 | 33 |
| The largest family, as a rerun (the reserve) | 7 (revocation; suspension and deletion) | 8 (creating and joining) | 5 (guest and anonymous; revocation) | 180 |
| Run 1 plus the reserve, against the caps | 18 of 20 | 26 of 30 | 6 of 10 | 785 of 5,000 |

It fitted, so run 1 could use the complete set's count. `EO-channel` can reserve one more channel if a probe creates the missing one; none did. After run 1 the session's ledger held 4 users, 2 channels and 57 calls; the reserve rerun of all 114 cases then fitted what was left (15 of 20 users, 20 of 30 channels), and used exactly the counted 11 users, 18 channels and a peak of 6 connections. The fakes' call count is not the live one (629 live in run 2).

### Live runs (26 September 2026, UTC; one checkout, one command at a time)

Every live command ran through a session launcher that starts `.venv/bin/python -m glow_stream_proof …` with an allowlisted environment (the path, home, proxy and CA variables, and the three `STREAM_*` variables), refuses `configure` with any option, `restore`, `cleanup` without `--apply`, and any other command, and refuses to start if an HDE variable is present. Each output was scanned before it was read: no output held the secret or a JWT-shaped string.

**Before run 1**, at `651c2df`:

- `verify-clean` (21:05:28–21:05:31), exit 1: "proof users remaining: []", "channels remaining: []", "other users present: 1", "user_groups remaining: []", and "polls remaining: not verified: HTTP 400 code 4". The poll listing's first live use (C2's `POST /api/v2/polls/query`) was refused, so no poll could be shown absent; everything else was as expected.
- Dry-run `configure` (21:07:00–21:07:02), exit 0: "differences before: []".

The record kept only the status and code, so commit `5df522c` keeps Stream's message for a listing that is not verified (offline, with a test and a reversal). Then, at `5df522c`:

- `verify-clean` (21:25:25–21:25:28), exit 1: as before, now with Stream's reason: "polls remaining: not verified: HTTP 400 code 4: QueryPolls failed with error: \"either user or user_id must be provided when using server side auth.\"". Server-side Query Polls needs a user; the only user that is not the proof's is the dashboard user, which the proof never uses, and whether a `user_id` narrows the listing to that user's polls is not documented. So the listing was not fixed in I2a (see "What I2b and P06.2 must know"). Earlier runs deleted the polls they created (DELETE 200, recorded above), and nothing points to a leftover poll, but none could be shown absent. I went on, reporting it here as the prompt asks ("report anything the harness marks 'not verified'").
- Dry-run `configure` (21:25:59–21:26:02), exit 0: "differences before: []", the same plan as at 21:07.

**Run 1**, from `5df522c`: `run --accept-dashboard-user`, prefix `p061i1-0926212611`, 21:26:11 to 21:26:20 (the launcher: 21:26:09 to 21:26:21), **exit 2**.

- Preflight: `{'dashboard_users_present': 1, 'configuration_problems': [], 'polls_before_run': 'not verified', 'user_groups_before_run': 0}`. The one-dashboard-user check with its creation minute passed at its first live use.
- Authorized path: AP1, AP2 (lifetimes, `exp` minus `iat`, 905 s: 900 s plus the SDK's 5 s back-dating), AP3-AB and AP3-XD PASS.
- **Stopped** before any case: "harness error: ClientSessionEnded: client A ended: reply id '{AB}' does not match command id 2". C1's reply matching, at its first live use, ended A's session at its first channel command. The cause is in "The defect run 1 found" below.
- Stop signals: none. Stops: none. Journal: nothing to restore.
- Usage: 4 users, 2 channels, 33 API calls (33 server, 0 client), a peak of 1 connection; the session's ledger then held 57 API calls (the four read-only checks before the run used 24).
- Cleanup: channels deleted (201, task completed); users deleted (201, task completed); the `deleted-user-1729640-…` user the delete created was found and deleted (201, task completed); no proof user, channel or `deleted-user` user remaining; user groups `[]`; polls not verified (the same 400 code 4).
- After the run: one problem, "remaining_polls: not verified: HTTP 400 code 4: QueryPolls failed with error: …". The final configuration check passed.

#### The defect run 1 found

`ClientSession.send` built each command as `{"id": <command id>, "op": …, "max_calls": …, **params}`. A channel command's parameters carry the channel as `id` (for example `type="glow-match", id="{AB}"`), which replaced the command's own `id`. The runner (`client/runner.cjs`) opened the channel with `cmd.id` and echoed `cmd.id` in its reply, so the reply's `id` was the channel's. Before C1 nothing compared the two, so I1's live runs worked. C1 added reply matching (`572c69d`), and no live run happened between C1 and I2a's run 1, where A's first channel command ended the session. The offline suite never saw it: the fakes replace `ClientSession`, and the tests that drive the real runner sent no channel command.

Fixed offline (`7ce93cc`): the channel travels as `channel_id`, and the command's `id` is set last, so no parameter can replace it (`client_bridge.py` `send` :277; `client/runner.cjs` :260). Two tests drive the real runner offline, with a development token made locally and a channel method that fails before any request: `tests/test_runner.py` `RunnerTest.test_a_channel_command_names_its_channel_as_channel_id` and `ChannelCommandSessionTest.test_a_channel_command_keeps_its_own_id_end_to_end`. With the Python side reverted, the second fails with the live message, "reply id 'proof-channel' does not match command id 2". An audit of every command the Python side sends found no other field the runner reads differently.

The prompt's rule for this case (section 5): "Fix harness errors offline, against the fakes, never by trying a live run"; and "Reserve: at most one rerun, `run --accept-dashboard-user --only <case ids>`, for cases run 1 could not complete. It must fit what the session has left." Run 1 completed no case, so the reserve rerun names all 114. It fits what the session had left: with the ledger's 4 users, 2 channels and 57 API calls, the complete set brings the session to 15 of 20 users, 20 of 30 channels, a peak of 6 of 10 connections, and about 662 of 5,000 API calls on the fakes (`checks/run_plan.py`, `session_used_before`). After it, no live run remains.

**Before the reserve rerun**, at `7ce93cc` (the offline checks passed and all 242 fix reversals were demonstrated at this commit, pushed):

- `verify-clean` (21:50:38–21:50:40), exit 1: the same as at 21:25 (no proof user or channel, one other user, no user group; polls not verified, with the same message).
- Dry-run `configure` (21:50:40–21:50:43), exit 0: "differences before: []", the same plan.

**The reserve rerun (run 2)**, from `7ce93cc`: `run --accept-dashboard-user --only <all 114 case IDs, in the matrix's order>`, prefix `p061i1-0926215052`, 21:50:52 to 21:55:46 (the launcher: 21:50:51 to 21:55:47), **exit 4** (completed; one problem after it, the poll listing).

- Preflight: one dashboard user, no configuration problem, polls not verified, no user group.
- Authorized path: all 25 checks PASS: AP1 to AP10 (17 checks), AP11 (disconnect, reconnect, watch and the next message received) and AP12 for each mechanism (the app send path refuses both members' sends after it, with no Stream call: the API-call count unchanged across the two sends).
- Cases: all 114 recorded. 82 HOLDS, 5 HOLDS (filtered, not refused), 3 HOLDS (accepted, not applied), 1 REFUSED (feature off; not a permission error), 13 FAIL, 4 INCONCLUSIVE, 5 DOES NOT MEET the history policy, and 1 RECORDED (a mapping). Every row is in "Results by topic" below.
- Stops: none. Stop signals: none. Every journalled temporary change (the channel-level feature overrides of S2, S5, S6, S7 and S15, the type-level toggles of S10, S12 and F9-ai, and guest creation for G1's control and G2's setup) was restored and verified; nothing was left unrestored or unverified.
- Usage (the run): 11 users, 18 channels, 629 API calls (353 server, 276 client), a peak of 6 connections, 41 connection attempts. The session's ledger afterwards: 15 of 20 users, 20 of 30 channels, 698 of 5,000 API calls, a peak of 6 of 10 connections.
- Notes the run recorded: client A's SDK sent `POST /channels/glow-match/{AB}/query` twice between commands (201), and M2's twice in `{CH_freeze}` (201), with M1's once more reported in its exit reply; M1 had one asynchronous error, "PROOF_BUDGET: request refused before sending (budget reached)", a request its SDK started during an `events` wait, refused before it was sent. Each was checked for a charge or limit signal (none) and counted.
- Cleanup: 2 polls deleted by recorded ID (200, 200); 1 user group deleted (200); channels deleted (201, task completed); users deleted (201, task completed), with no user found by prefix that was not recorded; the `deleted-user-1729640-…` user the delete created found and deleted (201, task completed); no proof user, channel or `deleted-user` user remaining; user groups `[]`; polls not verified.
- After the run: "remaining_polls: not verified: HTTP 400 code 4: QueryPolls failed with error: …", the only problem. The final configuration check passed.

**After the last run**, at `7ce93cc`:

- `verify-clean` (22:00:21–22:00:24), exit 1: "proof users remaining: []", "channels remaining: []", "other users present: 1", "user_groups remaining: []", "polls remaining: not verified: HTTP 400 code 4: QueryPolls failed with error: \"either user or user_id must be provided when using server side auth.\"".
- Dry-run `configure` (22:00:24–22:00:26), exit 0: "differences before: []", the same plan as before every run. There was nothing to decide.

Session totals: 15 of 20 users, 20 of 30 channels, 698 of 5,000 API calls, a peak of 6 of 10 connections. Nothing suggested a charge; no rate limit was met. The reserve is spent: no further run is available in this session.

**Commits after the last run, not exercised live:** the commit that adds this section, which changes only this record.

### Results by topic (run 2, `p061i1-0926215052`, from `7ce93cc`)

`{A}`, `{M1}`, `{CH_remove}` and the other braces stand for the run's synthetic identifiers. Every verdict below is the harness's, under the rules committed before the run; where my reading of a row differs from its recorded verdict, the row says so and why, and the verdict stands as recorded.

#### Revocation, suspension and deletion

For the member each mechanism acts on (M1 on the channel-level mechanisms; R and its second device R-2; S; H). "Ended" is Stream's authentication or permission error after the same request by the same member succeeded before; each family's controls before its mechanism succeeded for both members, so no earlier family had reached its channel.

| Case | Applied (server, through the guard) | REST read | Open subscription | Token reuse | Own member write (S15) | Token issued after | Member's own undo | History retained | Verdict |
|---|---|---|---|---|---|---|---|---|---|
| RV-remove | `POST /channels/glow-match/{CH_remove}` `remove_members: [{M1}]`, `user_id: {M2}` → 201 | ended (403 / 17) | ended (missed in both windows; M2 received it) | ended (connected; read 403 / 17) | not shown (404 / 16) | – | HOLDS (`addMembers` 403 / 17; server replay 201) | yes | **INCONCLUSIVE**: not shown, s15 for M1 |
| RV-ban | `POST /api/v2/moderation/ban` `target_user_id: {M1}`, `channel_cid`, `banned_by_id: {M2}` → 201 | not ended (201) | not ended | not ended (read 201) | not ended (200) | – | HOLDS (`unbanUser` 403 / 17; replay `DELETE` 200) | yes | **DOES NOT MEET** |
| RV-hide | `POST /channels/glow-match/{CH_hide}/hide` `user_id: {M1}` → 201 | not ended | not ended | not ended | not ended | – | **FAIL**: M1's `show` 201 (after the server hid it again: 201, "not listed") | yes | **DOES NOT MEET**, and the member's own client undid it |
| RV-freeze | `PATCH /channels/glow-match/{CH_freeze}` `frozen: true`, `user_id: {M2}` → 200 | not ended, for M1 and M2 | not ended, both | not ended, both | not ended, both | – | HOLDS (`updatePartial` 403 / 17; replay 200) | yes | **DOES NOT MEET** |
| RV-revoke | `PATCH /api/v2/users`, R's `revoke_tokens_issued_before` = 21:54:51Z → 200 | ended, R and R-2 (401 / 40) | ended, both (missed in both windows) | ended, both (connect 401 / 40) | ended, both (401 / 40) | **not ended**: issued 7 s after, `iat` 2 s after the revocation time; connect ok, read 201 | – | yes | **DOES NOT MEET** |
| SD-deactivate | `POST /api/v2/users/{S}/deactivate` `mark_messages_deleted: false` → 201 | not shown (404 / 16) | ended (missed in both windows) | not shown (connect 404 / 16) | not shown (404 / 16) | not shown (connect 404 / 16) | – | yes; S's own message kept, not deleted | **INCONCLUSIVE** |
| SD-delete | `POST /api/v2/users/delete` `user`, `messages`, `conversations` all `hard` → 201, task completed | not shown (404 / 16) | not shown (the channel was gone, so no probe could be sent) | ended (connected; read 403 / 17) | not shown (404 / 16) | ended (connected; read 403 / 17) | – | **no**: the delete removed the channel and its messages | **DOES NOT MEET**: the messages are not retained |

**Which mechanism meets the policy:** none, on its own. What each shows:

- **Removal** ends M1's REST read, its open subscription and reuse of its token; its own member write then got 404 code 16 ("does not exist"), which the rule does not count as a refusal, so the case is INCONCLUSIVE, not MEETS. M1's client cannot rejoin. M1's member custom data was not kept across removal and re-adding (`member_custom_after_readd`: absent).
- **A channel ban** ends none of the four: M1 still reads the channel and its history, still receives its events, still writes its own membership, and a new session with its token reads it. It stops M1 posting: the server-side send on M1's behalf was refused 403 code 17, "Your account is currently banned from chat."
- **Hide** only hides the channel from M1's channel list (not listed after it; listed again after a new message, as Stream documents), and M1's own client can show it again.
- **Freeze** stops new messages and reactions (Stream's documentation) but ends none of the four for either member.
- **Per-user revocation** ends every token issued before it: REST, WebSocket and S15 for both of R's devices, and the open subscriptions. A token issued at once (its `iat` back-dated 5 s by the server SDK, 5 s before the revocation time) was refused (connect 401 code 40), as designed; one issued 7 s later connected and read the channel. So revocation alone does not keep R out; the app's token issuance has to (P06.2).
- **Deactivation** answers every request and connect of S with 404 code 16 (the server-side send on S's behalf: "the user {S} was deactivated"), and S's open subscription stopped receiving; S's data is kept. Stream answers "does not exist", not an authentication or permission error, so under the rule the dimensions are "not shown" and the case INCONCLUSIVE.
- **The hard delete** removes the conversation (a channel of two members), so the history the policy keeps for safety reports is gone. After it, a connect with H's old token, and one with a token issued after the delete, both **succeeded** (`connected_after_the_delete`: `H`, `H-new`); that H was re-created is inferred from the connects' success, and no read of the user shows it (corrected in P06.1-I2b; the I2a review's nit 6). The channel read was then refused 403 code 17. The cleanup named H again.

**What each member was shown** (event types, the SDK's local events excluded; where M2 appears, member lists left out):

- Removal: M1 received `channel.kicked`, `channel.updated`, `member.removed`, `notification.mark_read` and `notification.removed_from_channel`; M2 received `channel.updated` and `member.removed`. M2 appears as the acting user in `channel.updated` (`user.id` and `user.name`), in both members' events.
- Ban: both received `user.banned`, naming M2 in `created_by.id` and `created_by.name`.
- Hide: M1 received `channel.hidden` and `notification.mark_read`; M2 nothing.
- Freeze: both received `channel.updated`; M2 appears only as the channel's creator (`channel.created_by`), not as the acting user.
- Revocation: nothing to any member.
- Deactivation: S received `user.deactivated`.
- Hard delete: H received `channel.deleted` and `user.deleted`; M2 `channel.deleted`.
- No mechanism added a system message.

**Send versus revocation:** `AP12-<mechanism>` PASSED for all seven: after the app recorded the unmatch or block, its send path refused both members' sends without calling Stream. Stream's answers to the server-side send on the affected member's behalf (an observation only): 201 after removal, hide, freeze and revocation; 403 code 17 after the ban; 404 code 16 after deactivation ("the user {S} was deactivated") and after the hard delete (the channel was gone).

**The subscription's window:** the second window (the independent review, point 2) was used live: after the removal M1 missed the probe in its first window and again in its second, as did R and R-2 after the revocation and S after deactivation, while the listener received it. No connection closed or recovered in any family's windows, so no subscription dimension was made "not shown" by that rule.

**Tokens:** each member's token had between 795 and 885 s left when its observations ended, well past the 60 s margin.

#### Tokens and devices, send, and outage

- **TD-expiry: HOLDS.** A second device of A with a 25 s token (`exp` minus `iat` 30 s, the SDK's back-dating included): before expiry it connected, watched and read (the read finished 23.8 s before `exp`); after expiry its read and its reconnect both got 401 code 40. Observations: its already-open connection **still received** the probe after the token expired, and A's first device still read AB.
- **OUT-send: HOLDS** (the outage injected in-process only: an `httpx` transport raising `ConnectError`, no address used). The app send path refused with the provider's connection error, kept no message ID, left the match state and the run's message record unchanged; a server-side read found no such message; the transport saw exactly one request; the same send with the provider reachable succeeded. No real outage is claimed.

#### The S15 mapping, pin and archive

- **S15: FAIL**, as in I1: A's member custom data (`glow_note`) reached B through B's channel query and B's `member.updated` events (and, with `read-channel-members` granted on AB, through B's members query too). The local-event filter (C1) was used: `channels.queried` was dropped, and the marker came in `member.updated`.
- **S15-map: RECORDED.** Of A's own member writes: `glow_note`, `pinned` and `archived` were accepted and stored, and B saw each (`member.updated`, and B's channel query); `notifications_muted`, `channel_role`, `is_moderator`, `banned`, `shadow_banned` and `invited` were refused 403 code 17. The server's replay of the refused ones: `channel_role` 200 and stored (so only the server can set it); the other five 403 code 17 **even server-side**. Every change was put back and the whole record verified (for example `channel_role`: "PATCH 200; verified True"; the refused fields: "nothing to put back; verified True"). The server's overwrite of A's `glow_note` was stored, and its clear removed it. The three `member_custom_on_*` settings read false.
- **F9-pin and F9-archive: FAIL.** A pinned (archived) AB for itself; the flag was stored, and B read it in its channel query (A's member record carries it) and in `member.updated`. A's record was put back and verified.

#### The finding-9 endpoints

| Case | A's request | A's answer | Control | Verdict | My reading |
|---|---|---|---|---|---|
| F9-replies | `GET /messages/{m_x}/replies` | 400 code 19: "Channel glow-match:{XD} does not support replies" | X: 400 code 19 | **FAIL**: response disclosed `{XD}` | A real disclosure: from a message ID alone, a non-member learns the message's channel (before any permission check; replies are off) |
| F9-reactions | `GET /messages/{m_x}/reactions` | 400 code 19: "… does not support reactions", naming `{XD}` | X: 400 code 19 | **FAIL**: response disclosed `{XD}` | The same disclosure |
| F9-by-id | `GET /channels/glow-match/{XD}/messages` | 403 code 17 (ReadChannel) | X: 200 | HOLDS | – |
| F9-query-reactions | `POST /messages/{m_x}/reactions` (`queryReactions`) | 403 code 17 | X: 201 | HOLDS | – |
| F9-thread | `GET /threads/{m_x}` | 404 code 16: "Thread with id \"{m_x}\" doesn't exist" | X: 404 code 16 | **FAIL**: response disclosed `{m_x}` | **Not a disclosure**: the only term found is the message ID A itself sent in the path; A and X got the same 404, which is not attributable. By the rule's purpose this reads INCONCLUSIVE |
| F9-history | `POST /messages/history` | 403 code 17: "this endpoint can only be called server side" | server replay 403 code 17: "this endpoint needs a feature flag, contact support to get it enabled" | INCONCLUSIVE | Enterprise only, as documented |
| F9-sync | `POST /sync` for XD's cid | 201; learned no channel, no message, no user | X: 201, found XD's data | **FAIL**: response disclosed `{XD}` | **Not shown to be a disclosure**: the only term found is XD's channel ID, which A's own request named; the row does not keep the response, so where it appeared is not recorded (getstream's `SyncResponse` has `inaccessible_cids`, which would echo it). Nothing of XD's was learned. By the rule's purpose this reads HOLDS (filtered, not refused) |
| F9-ai | `POST /channels/glow-match/{AB}/event` (`updateAIState` with `ai_message` free text) | 201, with custom events on and under the production configuration | server replay 201 | **FAIL**: succeeded under the production configuration | A member can send free text to the other as an AI-indicator event even with custom events off |
| F9-member-other | `PATCH /channels/glow-match/{AB}/member/{B}` (`glow_note` on B's membership) | 200 | server replay 200; undo 200 | **FAIL**: the client action succeeded | A's write to B's member record was accepted; whether Stream stored it was not read |
| F9-ban, F9-shadowban | `POST /moderation/ban`: A bans (shadow-bans) B in AB | 403 code 17 (BanChannelMember) | server replay 201; undo `DELETE` 200 | HOLDS | – |
| F9-leave | `POST /channels/glow-match/{AB}`: A leaves AB with a message | 403 code 17 (RemoveOwnChannelMembership) | server replay 201; undo 201 | HOLDS | – |
| F9-invite-accept, F9-invite-reject | B, invited to a channel of A's, accepts (rejects) with a message | 201 | – | **FAIL**: the text reached A in `channel.updated` and `message.new` and is stored in the channel | Invites answered with a message are a free-text path to the other member |

The two rows whose recorded FAIL I read otherwise (F9-thread and F9-sync) follow the disclosure rule as written before the run: a response that contains a target term is a disclosure, including a term the request itself carried. I did not change the rule after seeing the results: that would be a rule changed after the run, in the direction that removes FAILs. It is for the manager to decide, with I2b ("What I2b and P06.2 must know").

#### The existence oracle

- **EO-message: FAIL.** `getMessage` for XD's existing message got 403 code 17; for a message ID that does not exist, 404 code 16. A non-member can tell whether a message ID exists.
- **EO-channel: FAIL.** The documented Get Channel (`GET /channels/glow-match/{id}` through the runner's `get` op) got 403 code 17 for XD and 404 code 16 for a channel that does not exist: a channel-existence oracle (Stream documents the 404). A's `query` and `watch` got 403 code 17 for both; the pairs were judged different on Stream's message text, with the IDs replaced. The row keeps only status and code, so what differed in the text is not recorded; the query and watch pairs' FAIL rests on the harness's comparison alone. The GET pair's FAIL stands on status and code.
- **EO-user: HOLDS.** `queryUsers` returned 200 for both IDs, with the same keys and size, and adding either user to AB got 403 code 17.
- No probe created the missing channel.

#### G2 and S10 (new setups, first live runs)

- **G2:** Stream refused the server-side guest creation while guest creation was disabled (403 code 17); guest creation was enabled for that moment (200), the guest created (201) and creation disabled again and verified. Stream stored the guest as `guest-<id>-{prefix}-g2`, role `guest`, and it connected by its ID with role `guest`. G2-read-ab HOLDS (403 code 17: role `guest` may not ReadChannel), G2-channels HOLDS (403 code 70), G2-users HOLDS (filtered, not refused), G2-message HOLDS (403 code 17). I1 could not run G2.
- **S10: HOLDS.** With polls on for the type, the server's poll message in S10's own channel was accepted, and A's vote was refused 403 code 17 (CastVote) with polls on and again under the production configuration; the server's identical vote succeeded. Polls were turned off again and verified.

#### The I1 matrix, rerun

Of the 85 I1 cases, 76 have the verdict I1's final run recorded, and 9 changed, each for a reason recorded before the run:

- **G1-create, G3-channels and R9:** INCONCLUSIVE in I1 (their controls did not succeed) → HOLDS, their controls now succeeding (C1's control fixes; the I1 review's runs had already shown these three).
- **G2-read-ab, G2-channels, G2-users and G2-message:** not run in I1 → HOLDS, HOLDS, HOLDS (filtered), HOLDS (G2's new setup).
- **S10:** INCONCLUSIVE → HOLDS (S10's new setup).
- **RT2:** HOLDS in I1 → REFUSED (feature off; not a permission error), 400 code 18, by the manager's decision on C2, as C3's record anticipated.

S15 is FAIL, as in I1. R7a is INCONCLUSIVE, as in I1 (400 code 4, "There are no searchable channels"). T4-ws, T4-rest-unread and E5 are HOLDS (accepted, not applied), as in I1. RT3 HOLDS: A's `markRead` was delivered to B as `message.read` without the free-text field, so its control was not needed.

### First live use of the earlier fixes

For each item on the three "What P06.1-I2a must know" lists (C1's, C2's and C3's), what the live runs showed. "Not exercised" means neither run reached it; it stays untested live.

**C1's list:**

- **The answer-based verdicts:** used throughout run 2; every verdict names Stream's status and code.
- **The journal, restore retries and the final `configuration.verify()`:** every journalled change was restored and verified at its case's end (nothing reached the end of the run); the final configuration check passed after both runs. Restore retries were not needed: not exercised.
- **The one-dashboard-user preflight with its creation-minute check:** passed in both runs ("dashboard_users_present": 1).
- **Reply matching: failed at its first live use** (run 1): a channel command's `id` replaced the command's own, so the check ended the session at the first channel command. Fixed in `7ce93cc` ("The defect run 1 found"); run 2 then used it for every client command without a mismatch.
- **The local-event filter:** used; S15's marker came in `member.updated`, with `channels.queried` dropped.
- **The typed-call charge hook:** the typed calls (`upsert_users`, `get_or_create_channel`, `send_message`) ran live; no charge signal came, so the hook's stop was not exercised.
- **Cleanup's judgement:** used after both runs; its only problem was the poll listing.
- **`restore --apply`'s verification:** not exercised (the prompt forbids `restore --apply`).
- **New server calls:**
  - `POST /api/v2/chat/channels` filtered by `cid` (the override re-reads): answered 2xx. While a channel-level override was set, the channel read showed it as the value in `config` (`has_config_overrides` false: no `config_overrides` key), so each override's key was "shown while set" (S2 `replies`, S5 `reactions`, S6 and S7 `uploads`, S15 `grants`), and each read clear after its removal. Key names recorded: the channel's `blocked`, `cid`, `config`, `created_at`, `created_by`, `custom`, `disabled`, `frozen`, `hidden`, `id`, `last_message_at`, `member_count`, `own_capabilities`, `type`, `updated_at`; `config` held the type's feature keys (`grants` too while the S15 grant was set).
  - `GET /api/v2/usergroups`: 200 with `user_groups` (empty before and after the runs).
  - `POST /api/v2/polls/query`: **400 code 4**, "QueryPolls failed with error: \"either user or user_id must be provided when using server side auth.\"" Polls are "not verified" at preflight, after the run and in `verify-clean`, and each run exited 4 for it.
- **Preflight's stop on the creation time:** not triggered.
- **Exit codes of `run`:** run 1 exited 2 (stopped), run 2 exited 4 (completed, a problem after it); the printed "after the run" line named it.
- **`member.updated`:** `marker_event_types` named `member.updated` in S15.
- **G2 and S10:** both ran with their new setups and HOLD ("G2 and S10").
- **Budget:** the matrix never came near its stop (629 calls in run 2).

**C2's list:**

- **An interrupted case records its row:** no case was interrupted in run 2; run 1 stopped outside the matrix. Not exercised.
- **T4-rest-unread** HOLDS (accepted, not applied), with both controls and all three totals (A's own total 0, B's own total 1).
- **RT2 and RT3 on a refusal:** superseded by C3's rule (below).
- **A feature-gated case, and S10, without a production answer:** every production request was answered. Not exercised.
- **One request per command; G1's `POST /guest` the only request:** G1-create HOLDS; no command in run 2 recorded more than one request.
- **E5 and S14 with an unreadable stored user:** A's stored user was read (E5: stored role `user`). Not exercised.
- **A failed restore of A's role in E5:** not triggered.
- **Stop and restore rules** (a rate limit retried at the end of the run; an accepted removal that cannot be verified is "not verified"): no signal and no unverifiable removal. Not exercised.
- **Outputs:** `run-<prefix>.json` was written before the end of each run and again after it; `run-<prefix>-progress.json` after every case; `client_success_undo` appears in rows (F9-member-other: "undo PATCH 200"; F9-ai: "none defined", an event cannot be undone); no second Ctrl-C.
- **The `rate_limited` flag on Stream's real 429 and code-9 answers, and call counts after a charge signal:** not exercised (none came).

**C3's list:**

- **RT2, feature refusal:** RT2 read REFUSED (feature off; not a permission error), 400 code 18.
- **RT3's control against Stream's real `markRead`:** not exercised: A's `markRead` succeeded and reached B without the free-text field, so RT3 HOLDS on that branch and needs no control.
- **A feature-gated case's FAIL when the enabling request fails:** every enabling request was answered 2xx. Not exercised.
- **E5 and S14's stop:** not triggered.
- **S15's unset after a guardrail stop or a signal:** not triggered; S15's unset was sent (its control reads "member field unset (200, 200)").
- **Stop rules (a signal anywhere skips the cleanup; no undo or unset after a signal):** no signal. Not exercised.
- **Outputs:** the results carry `stop_signals` (empty); no row carries `requests` (no command recorded more than one request) or `member_field_unset` (S15's unset was sent).

**Step 1's own items, first live use:** the guard ran on every server request of both runs and refused none of the runs' own; `cleanup --apply` was not needed. The runner reported requests the SDK sent between commands, and one asynchronous error, and the harness checked and counted them. The closing checks compared every recorded application setting before and after each run, with no difference. The signal-by-kind rules were not exercised.

**The answer shapes of the new I2a server calls** (key names only): the ban `duration`; the member removal and the freeze `channel`, `duration`, `members`; the hide `duration`; the per-user revocation `duration`, `membership_deletion_task_id`, `users`; the deactivation `duration`, `user`; the hard delete `duration`, `task_id`. The server-side guest creation (`POST /guest`): the harness read `user.id`, `user.role` and `access_token` (never printed or written); other keys were not recorded. The member read (`GET /api/v2/chat/members`) answered with `members`; the runner's GET (`GET /channels/glow-match/{id}`) answered 403 code 17 or 404 code 16.

### Records corrected

In this record, each claim was false at C1's head and is corrected in place, marked "(corrected in P06.1-I2a)"; the protected sections are unchanged byte for byte:

- **C1's finding 5 row** ("Replies matched to commands", Fixed): at its first live use the check ended the session at the first channel command, because a channel command's `id` replaced the command's own.
- **C1's nit 13 row** ("verify-clean lists polls and user groups"): at its first live use Stream refused the poll listing (400 code 4, a user is needed server-side), so polls are reported not verified.

In `proofs/stream-chat/README.md` (committed with the code; the listing and runner corrections before run 2): the runner's row in "Layout" (a channel command's `channel_id`, "corrected in P06.1-I2a"); the limits bullet on the listings (the poll listing's first live use); and every rule of step 2 and of the independent check's fixes.

### Checks

Run from `proofs/stream-chat/` unless noted, at the code head `7ce93cc` (the head of the reserve rerun), in clean processes (`env -i`) with no `STREAM_*` variable, except the live commands.

| # | Check | Result |
|---|---|---|
| 1 | `git diff --check 6e67fd6… 7ce93cc…` (repository root) | No output, exit 0 |
| 1 | `git diff --name-only 6e67fd6… 7ce93cc…` | 40 paths, all under `proofs/stream-chat/` (all owned): 28 changed, 12 new (`checks/run_plan.py`, `client/request-log.cjs`, `glow_stream_proof/guard.py`, `i2a.py`, `mechanisms.py`, `stops.py`, and `tests/fake_world.py`, `test_closing_checks.py`, `test_guard.py`, `test_i2a.py`, `test_mechanisms.py`, `test_run_plan.py`). No dependency file, lock, `package*.json`, `.npmrc`, `pyproject.toml` or baseline change. All 64 files under `proofs/stream-chat/` have mode 100644; no symlink or executable. +8,807 and −244 lines. The commit adding this section changes only this record |
| 2 | The trusted policy from `origin/main` (`0f45e64`), extracted to a directory outside the tree and run with system Python 3.11.15: `python3 -I change_scope.py --base 6e67fd6… --head 7ce93cc… --merge-base` | Exit 0; `{"full": true, "reason": "behavior-or-empty", …}`, 40 paths. One merge base, `6e67fd6`. Full scope, as expected |
| 3 | In a new directory, from the unchanged lock files: `python3.12 -m venv .venv`; `pip install --require-hashes -r requirements-dev.lock`; `pip check`; `npm ci --ignore-scripts`; proxy and CA variables passed by reference | Exit 0; "No broken requirements found."; npm "found 0 vulnerabilities". `getstream` 6.1.0, Ruff 0.16.8, mypy 2.3.1, `stream-chat` 9.53.0. The lock and dependency files are unchanged from `6e67fd6` to `7ce93cc` |
| 4 | `env -i PATH="$PATH" HOME="$HOME" LANG=C.UTF-8 .venv/bin/python -m unittest discover -s tests -t .`, on a clean export of each commit using that install | At the start (`6e67fd6`): `Ran 252 tests`, `OK`. At step 1's commit (`f3ef40b`): `Ran 301 tests`, `OK`. At the code head: `Ran 393 tests`, `OK` |
| 4 | `ruff check .` / `ruff format --check .` / `mypy` at the code head | "All checks passed!" / "51 files already formatted" / "Success: no issues found in 49 source files" |
| 4 | `node --check` on `client/runner.cjs`, `client/error-info.cjs` and `client/request-log.cjs` | Exit 0, each |
| 5 | `.venv/bin/python checks/fix_reversals.py <scratch dir>` | At the start (`6e67fd6`, its own script): "reversals: 147, not demonstrated: 0". At step 1's commit: "reversals: 186, not demonstrated: 0". At the code head: **"reversals: 242, not demonstrated: 0"**, exit 0: C1's 51, C2's 48, C3's 48, and 95 for I2a (39 at step 1; 56 for step 2, the independent check's findings and the two fixes made during live work). Every edited file loaded, and no reversal failed through a syntax or import error. 206 failed on an assertion, and 33 on the error the reverted fix causes (for example a `KeyError` on a missing detail, `ClientSessionEnded` with the live message "reply id 'proof-channel' does not match command id 2", or the injected stop propagating); three by a Ctrl-C that aborts the test process, by design (C1's "F2 Ctrl-C handled", C2's "nit 8 second Ctrl-C inside finish()" and "a Ctrl-C during the early write still reaches the restores"). I read each failure reason; the table below lists them. The same run passed at `651c2df` (239) and `5df522c` (240) before each live step |
| 6 | Secret scan of `git diff 6e67fd6… 7ce93cc…` (537,053 bytes) and of every kept output (the runs' `.work` files and the live commands' outputs, 19 files) | The diff: the application secret 0; the API key 0; JWT-shaped strings 0; email addresses 0; private-key blocks 0; AWS-style keys 0; GitHub or other token formats 0; TLS-weakening settings 0; environment dumps 0. The outputs: the secret 0 and JWT-shaped strings 0; the application's API key appears twice, in run 2's local results (`.work`, ignored and never committed), inside Stream's own error message for T2-ws's wrong-signature token ("… created using the secret for API key …"); it is not quoted here |
| 7 | The live commands (section "Live runs") | Before each run: `verify-clean` and the dry-run `configure`; after the last: both again. Every output scanned before it was read |
| – | The eight protected sections of this record, compared with `6e67fd6` | Byte-identical |

Not run: hosted CI (this session opened no pull request and triggered nothing); `configure --apply`, `restore --apply` and `cleanup --apply` (no run left anything to clean).

#### Each fix reversal at the code head

From `checks/fix_reversals.py`'s output at `7ce93cc`, in its order. Each reversal failed as listed with its fix reverted and passed with the fix restored. Long reasons are cut at 150 characters, and at most three failing tests are shown per reversal.

| # | Reversal | How its tests failed with the fix reverted |
|---|---|---|
| 1 | F1 request under test (generic) | `test_sdk_error_without_a_request_has_no_answer`: AssertionError: 'permission' != 'no-response'; `test_generic_case_uses_the_record_not_the_sdk_error`: AssertionError: 'HOLDS' != 'FAIL'; `test_generic_case_without_a_request_is_inconclusive`: AssertionError: 'HOLDS' != 'INCONCLUSIVE' |
| 2 | F1 G1 | `test_g1_fails_whenever_the_clients_post_guest_created_a_guest`: AssertionError: 'HOLDS' != 'FAIL' |
| 3 | F1 G3 | `test_g3_is_inconclusive_unless_the_anonymous_connect_succeeded`: AssertionError: 'anonymous connect' not found in 'no answer recorded (error: rethrown connect error)' |
| 4 | F1 RT2/RT3 | `test_rt2_local_throw_is_inconclusive`: AssertionError: 'refusal not attributable (no-response)' != 'no answer from Stream was recorded for the request under test'; `test_rt3_null_return_without_a_request_is_inconclusive`: AssertionError: 'refusal not attributable (no-response)' != 'no answer from Stream was recorded for the request under test' |
| 5 | F2 RunStopped re-raised | `test_failed_restore_stops_the_run`: AssertionError: RunStopped not raised |
| 6 | F2 try before enabling (type/channel) | `test_journal_entry_exists_before_the_enabling_request`: glow_stream_proof.stops.GuardRefused: guard refused PUT channeltypes/{id}: not a journalled temporary toggle of the match type |
| 7 | F2 try before enabling (guest) | `test_guest_creation_is_restored_after_an_interrupt_before_the_control`: glow_stream_proof.stops.GuardRefused: guard refused PATCH app: not a journalled temporary setting |
| 8 | F2 guardrail in flight kept | `test_restore_failure_does_not_hide_a_guardrail_stop_in_flight`: glow_stream_proof.stops.RunStopped: could not restore glow-match features {'custom_events': False}: PUT 500, re-read 200, differing {'custom_events': … |
| 9 | F2 end of run: journal, cleanup, verify, exit | `test_configuration_difference_after_the_run_exits_non_zero`: AssertionError: 0 != 4; `test_cleanup_problem_exits_non_zero`: AssertionError: 0 != 4; `test_ctrl_c_restores_cleans_up_writes_results_and_exits_non_zero`: AssertionError: Lists differ: ['guest user creation enabled'] != [] |
| 10 | F2 Ctrl-C handled | the test process stopped before reporting: KeyboardInterrupt |
| 11 | F3 exactly one | `test_no_dashboard_user_stops_the_run_when_one_is_expected`: IndexError: list index out of range; `test_two_dashboard_users_stop_the_run`: AssertionError: RunStopped not raised |
| 12 | F3 created_at | `test_another_creation_time_stops_the_run`: AssertionError: RunStopped not raised |
| 13 | F4 local events dropped | `test_local_query_event_is_not_counted_as_delivered`: AssertionError: True is not false; `test_marker_only_in_a_local_event_is_not_delivered`: AssertionError: 'FAIL' == 'FAIL' |
| 14 | nit 1 every window | `test_marker_in_another_event_type_in_the_second_window_fails`: AssertionError: 'HOLDS (accepted, not applied)' != 'FAIL' |
| 15 | nit 1 every event type | `test_marker_in_another_event_type_in_the_second_window_fails`: AssertionError: 'HOLDS (accepted, not applied)' != 'FAIL' |
| 16 | F5 reply id checked | `test_mismatched_reply_ends_the_session`: AssertionError: ClientSessionEnded not raised |
| 17 | F5 timeout ends session | `test_timeout_ends_the_session_and_releases_the_connection`: RuntimeError: no reply within 0.5s |
| 18 | F5 buffered line (select reader) | `test_buffered_line_is_read_without_a_timeout`: glow_stream_proof.client_bridge.ClientSessionEnded: client fake ended: no reply within 1.0s |
| 19 | F6 simulation guest connect refused | `test_guest_reach_runs_on_a_guest_created_server_side`: AssertionError: 'guest connect 403 / code 17' not found in 'identical request with guest creation enabled (201): POST /guest 201; guest connect ok (su… |
| 20 | F7 leak terms | `test_channel_object_without_text_is_a_leak`: AssertionError: 'INCONCLUSIVE' != 'FAIL'; `test_terms`: AssertionError: '{AB}' not found in {'{m_b_text}', '{m_a_text}'} |
| 21 | nit 2 code 2 | `test_api_key_error_is_not_a_token_refusal`: AssertionError: 'auth' != 'other' |
| 22 | nit 3 user_id from params | `test_no_user_id_is_not_invented`: AssertionError: 'user_id' unexpectedly found in 'POST /channels/glow-match/{XD}/query ?user_id={X}' |
| 23 | nit 4 undo checked | `test_failed_undo_stops_the_run_after_its_case`: AssertionError: RunStopped not raised |
| 24 | nit 4 member field unset checked | `test_member_field_unset_is_checked`: AssertionError: RunStopped not raised |
| 25 | nit 4 removal re-read | `test_removal_that_did_not_apply_stops_the_run`: AssertionError: RunStopped not raised |
| 26 | nit 4 removal status checked | `test_removal_refused_stops_the_run`: AssertionError: RunStopped not raised |
| 27 | nit 5 cleanup steps guarded | `test_a_failing_step_does_not_stop_the_others`: RuntimeError: connection reset |
| 28 | nit 5 task status judged | `test_task_that_does_not_complete_is_a_problem`: AssertionError: "channels_task is 'failed', not 'completed'" not found in [] |
| 29 | nit 6 typed-call charge signal | `test_typed_calls_stop_on_a_charge_signal`: KeyError: 'duration' |
| 30 | nit 7 request op removed | `test_unused_request_op_is_gone`: AssertionError: "Both secret and user tokens are not set.[68 chars]lled" != 'unknown op request' |
| 31 | nit 8 baseline written without users | `test_baseline_writes_no_other_users_identifier_or_name`: AssertionError: 'private-user-id' unexpectedly found in '{"app": {"app": {"allow_multi_user_devices": false, "custom_action_handler_url": "", "disable… |
| 32 | nit 8 redaction by pattern | `test_sensitive_keys_are_matched_by_pattern`: AssertionError: 'plain' != '<redacted-secret>' |
| 33 | nit 9 verify required settings | `test_verify_checks_permission_version_and_member_custom_settings`: AssertionError: False is not true : permission_version |
| 34 | nit 10 restore verified | `test_restore_apply_verifies_what_it_restored`: AssertionError: 0 != 1 |
| 35 | nit 11 isomorphic-ws check | `test_stream_chat_uses_the_runners_websocket`: AssertionError: False is not true : {'id': 1, 'ok': False, 'data': None, 'error': {'status': None, 'code': None, 'message': 'unknown op selfcheck', 'k… |
| 36 | nit 12 cleanup reserve | `test_reserve_covers_the_worst_case_end_of_run`: AssertionError: 115 not less than or equal to 60 |
| 37 | nit 13 client-created data tracked | `test_client_created_poll_and_group_are_deleted`: AssertionError: '/polls/client-poll' not found in {'/polls/p1'} |
| 38 | nit 13 verify-clean lists polls and groups | `test_verify_clean_lists_polls_and_user_groups`: KeyError: 'remaining_polls' |
| 39 | nit 15 check evidence redacted | `test_check_evidence_is_redacted`: AssertionError: '<jwt>' unexpectedly found in 'got <jwt>' |
| 40 | nit 16 E5 connection role | `test_e5_role_carried_by_the_connection_fails`: AssertionError: 'HOLDS (accepted, not applied)' != 'FAIL' |
| 41 | nit 16 S14 connection profile | `test_s14_profile_carried_by_the_connection_fails`: AssertionError: 'INCONCLUSIVE' != 'FAIL' |
| 42 | nit 16 T4-rest-unread controls | `test_unread_refusal_without_its_controls_is_inconclusive`: AssertionError: 'HOLDS' != 'INCONCLUSIVE' |
| 43 | review 1: a re-read proves a removal only if it showed the override | `test_re_read_that_never_shows_the_override_is_recorded_not_verified`: AssertionError: "not verified: ['replies']" not found in 'override removed (200; replies re-read clear)' |
| 44 | review 1: an ended B session leaves the grant unverified | `test_grant_unverifiable_when_bs_session_has_ended`: glow_stream_proof.stops.RunStopped: restore failed: config_overrides ['grants'] on AB: ClientSessionEnded: client B ended: no reply within 60s |
| 45 | review 2: a failed restore keeps the observed row | `test_failed_restore_stops_the_run`: AssertionError: 'interrupted before the case finished: the run stopped during this case' != 'the restore failed before the production phase' |
| 46 | review 3: S15's unset never hides a guardrail stop | `test_guardrail_stop_survives_a_failing_unset`: AssertionError: GuardrailStop not raised |
| 47 | review 4: polls and groups present at preflight are not leftovers | `test_only_new_ones_are_leftovers`: AssertionError: Lists differ: ['older-poll', 'run-poll'] != ['run-poll'] |
| 48 | review 5: journalled restores are retried | `test_restore_is_retried`: AssertionError: 1 != 3 |
| 49 | review nit: an unanswered anonymous connect is not a KeyError | `test_later_probes_are_inconclusive`: AssertionError: 'the anonymous connect did not answer' not found in "harness error: KeyError: 'anonymous'" |
| 50 | review nit: verify_restored checks automod and message length | `test_verify_restored`: AssertionError: Lists differ: [] != ['team.max_message_length is 1, want 5000'] |
| 51 | review nit: runner reports ws-api only for Stream's frame | `test_kinds`: AssertionError: 'ws-api' != 'ws-failure' |
| 52 | C2 F1 an interrupted case keeps what it observed | `test_s2_fail_survives_a_timeout_in_the_production_phase`: AssertionError: 'INCONCLUSIVE' != 'FAIL'; `test_s15_leak_survives_bs_session_ending_during_the_control`: AssertionError: 'INCONCLUSIVE' != 'FAIL'; `test_s3a_fail_is_recorded_when_the_replay_hits_a_rate_limit`: AssertionError: 'INCONCLUSIVE' != 'FAIL'; and 17 more |
| 53 | C2 F1 a guardrail stop records the case | `test_guardrail_stop_with_nothing_observed_records_an_inconclusive_row`: AssertionError: []; `test_s3a_fail_is_recorded_when_the_replay_hits_a_rate_limit`: AssertionError: []; `test_guardrail_stop_survives_a_failing_unset`: AssertionError: Lists differ: [] != ['S15'] |
| 54 | C2 F1 Ctrl-C records the case | `test_ctrl_c_with_nothing_observed_records_an_inconclusive_row`: AssertionError: []; `test_s3a_undo_is_not_made_after_ctrl_c`: AssertionError: [] |
| 55 | C2 F1 the owed undo after an interrupted control | `test_s3a_fail_is_recorded_when_the_replay_hits_a_rate_limit`: KeyError: 'client_success_undo'; `test_s3a_client_success_is_undone_after_a_replay_error`: KeyError: 'client_success_undo'; `test_s3a_undo_is_not_made_after_ctrl_c`: KeyError: 'client_success_undo' |
| 56 | C2 F1 no undo after a guardrail stop | `test_s3a_fail_is_recorded_when_the_replay_hits_a_rate_limit`: AssertionError: False is not true |
| 57 | C2 F1 the undo after a completed control is recorded | `test_undo_after_a_completed_control_is_recorded`: KeyError: 'client_success_undo' |
| 58 | C2 F1 kept: the client's request before its control | `test_s3a_fail_is_recorded_when_the_replay_hits_a_rate_limit`: AssertionError: 'INCONCLUSIVE' != 'FAIL'; `test_an_observed_refusal_becomes_inconclusive_with_the_interruption_as_reason`: AssertionError: 'not judged: client X ended: no reply within 60s' != '403 / code 17' |
| 59 | C2 F1 kept: the feature-on phase (S2) | `test_s2_fail_survives_a_timeout_in_the_production_phase`: KeyError: 'feature_override' |
| 60 | C2 F1 kept: bad-token REST | `test_t2_rest_success_survives_as_controls_session_ending`: AssertionError: 'INCONCLUSIVE' != 'FAIL' |
| 61 | C2 F1 kept: bad-token WebSocket | `test_t4_ws_connection_as_b_survives_a_failed_disconnect`: AssertionError: 'INCONCLUSIVE' != 'FAIL' |
| 62 | C2 F1 kept: T4-rest-xd | `test_t4_rest_xd_success_survives_xs_session_ending`: AssertionError: 'INCONCLUSIVE' != 'FAIL' |
| 63 | C2 F1 kept: G1 | `test_g1_created_guest_survives_a_failed_disconnect`: AssertionError: 'INCONCLUSIVE' != 'FAIL' |
| 64 | C2 F1 kept: guest and anonymous probes | `test_g3_leak_survives_the_controls_session_ending`: AssertionError: 'INCONCLUSIVE' != 'FAIL' |
| 65 | C2 F1 kept: S10 with polls on | `test_s10_vote_success_survives_an_error_in_the_server_replay`: AssertionError: 'INCONCLUSIVE' != 'FAIL' |
| 66 | C2 F1 kept: S10 before the production vote | `test_s10_polls_on_control_survives_the_production_vote_ending`: AssertionError: 'control not completed' != 'server replay POST -> 201' |
| 67 | C2 F1 kept: S15 under production | `test_s15_leak_survives_bs_session_ending_during_the_control`: AssertionError: 'INCONCLUSIVE' != 'FAIL' |
| 68 | C2 F1 kept: S14's connection | `test_s14_profile_on_the_connection_survives_a_failed_disconnect`: AssertionError: 'INCONCLUSIVE' != 'FAIL' |
| 69 | C2 F1 kept: S14's stored state | `test_s14_stored_change_survives_an_error_in_the_control`: AssertionError: 'INCONCLUSIVE' != 'FAIL' |
| 70 | C2 F1 kept: E5's connection | `test_e5_role_on_the_connection_survives_a_failed_disconnect`: AssertionError: 'INCONCLUSIVE' != 'FAIL' |
| 71 | C2 F1 kept: RT2/RT3 first window | `test_rt2_marker_in_the_first_window_survives_bs_session_ending`: AssertionError: 'INCONCLUSIVE' != 'FAIL' |
| 72 | C2 F1 kept: RT1 | `test_rt1_xd_event_survives_xs_session_ending`: AssertionError: 'INCONCLUSIVE' != 'FAIL' |
| 73 | C2 F2 T4-rest-unread needs both controls and all totals | `test_as_own_control_refused_is_inconclusive`: AssertionError: 'HOLDS (accepted, not applied)' != 'INCONCLUSIVE'; `test_a_missing_total_is_inconclusive`: AssertionError: 'HOLDS (accepted, not applied)' != 'INCONCLUSIVE'; `test_b_count_with_as_control_failed_is_inconclusive`: AssertionError: 'FAIL' != 'INCONCLUSIVE' |
| 74 | C2 F3 RT2/RT3 hold on attributable refusals only | `test_input_not_found_and_other_refusals_are_inconclusive`: AssertionError: 'HOLDS' != 'INCONCLUSIVE' |
| 75 | C2 F3 named events count only after an accepted request | `test_named_events_after_an_unattributable_refusal_are_inconclusive`: AssertionError: 'HOLDS' != 'INCONCLUSIVE' |
| 76 | C2 nit 4 only a rate limit is retried | `test_a_charge_signal_is_not_retried`: AssertionError: 3 != 1 : HTTP 402 |
| 77 | C2 nit 4 what counts as a rate limit | `test_charge_signals_are_not_rate_limits`: AssertionError: True is not false |
| 78 | C2 nit 4 flag on typed server calls | `test_rate_limits`: AssertionError: False is not true |
| 79 | C2 nit 4 flag on raw server calls | `test_the_result_check_flags_a_rate_limit`: AssertionError: False != True : 429 |
| 80 | C2 nit 4 flag on client requests | `test_flags`: AssertionError: False is not true |
| 81 | C2 nit 5 production phase needs an answer (feature-gated) | `test_feature_gated_case_without_a_production_answer_is_inconclusive`: AssertionError: 'HOLDS' != 'INCONCLUSIVE' |
| 82 | C2 nit 5 production phase needs an answer (S10) | `test_poll_vote_without_a_production_answer_is_inconclusive`: AssertionError: 'HOLDS' != 'INCONCLUSIVE' |
| 83 | C2 nit 6 exactly one request | `test_two_recorded_requests_have_no_answer`: AssertionError: 'permission' != 'no-response'; `test_generic_case_with_two_requests_is_inconclusive`: AssertionError: 'HOLDS' != 'INCONCLUSIVE' |
| 84 | C2 nit 6 G1's one POST /guest | `test_guest_attempt_with_another_request_has_no_answer`: AssertionError: 'HOLDS' != 'INCONCLUSIVE' |
| 85 | C2 nit 7 E5 with an unreadable stored user | `test_e5_is_inconclusive_when_as_stored_user_cannot_be_read`: AssertionError: 'HOLDS (accepted, not applied)' != 'INCONCLUSIVE' |
| 86 | C2 nit 7 S14 with an unreadable stored user | `test_s14_is_inconclusive_when_as_stored_user_cannot_be_read`: AssertionError: 'HOLDS (accepted, not applied)' != 'INCONCLUSIVE' |
| 87 | C2 nit 7 the stored user is matched by ID | `test_server_user_matches_the_id`: AssertionError: {'id': 'someone-else', 'role': 'admin'} is not None; `test_e5_is_inconclusive_when_as_stored_user_cannot_be_read`: AssertionError: RunStopped not raised |
| 88 | C2 nit 8 second Ctrl-C inside finish() | the test process stopped before reporting: KeyboardInterrupt |
| 89 | C2 nit 8 results written before the end of the run | `test_results_are_written_before_the_end_of_the_run`: StopIteration |
| 90 | C2 nit 9 accepted but unverified is not 'not restored' | `test_at_the_end_of_the_run`: AssertionError: Lists differ: [TemporaryChange(description="config_overr[1284 chars]t())] != []; `test_during_a_case`: AssertionError: Lists differ: [TemporaryChange(description="config_overr[1284 chars]t())] != [] |
| 91 | C2 nit 9 B's probe stopped by a guardrail leaves the removal unverified | `test_at_the_end_of_the_run`: AssertionError: Lists differ: [TemporaryChange(description="config_overr[1140 chars]t())] != []; `test_during_a_case`: AssertionError: Lists differ: [TemporaryChange(description="config_overr[1140 chars]t())] != [] |
| 92 | C2 nit 10 credential key names | `test_credential_keys_of_the_app_settings_model_are_redacted`: AssertionError: False is not true : firebase_server_key |
| 93 | C2 review: E5 keeps a stored-role FAIL before its restore | `test_e5_stored_role_fail_survives_a_rate_limited_restore`: AssertionError: 'INCONCLUSIVE' != 'FAIL' |
| 94 | C2 review: E5's failed restore stops the run | `test_e5_failed_restore_stops_the_run_after_its_row`: AssertionError: RunStopped not raised |
| 95 | C2 review: a failing progress write never replaces the stop | `test_a_failing_progress_write_never_replaces_a_guardrail_stop`: OSError: disk full; `test_ctrl_c_is_kept_when_the_progress_write_fails`: OSError: disk full |
| 96 | C2 review: a key still overridden keeps the change journalled | `test_a_key_still_overridden_keeps_the_change_journalled`: glow_stream_proof.usage.GuardrailStop: guardrail: api_calls would be passed; stopping before the call |
| 97 | C2 review: finish keeps its problems as it finds them | `test_finish_keeps_the_problems_found_before_a_second_ctrl_c`: AssertionError: False is not true |
| 98 | C2 review: results files are written atomically | `test_a_failed_write_leaves_the_previous_file_whole`: json.decoder.JSONDecodeError: Expecting value: line 1 column 1 (char 0) |
| 99 | C2 review: a Ctrl-C during the early write still reaches the restores | the test process stopped before reporting: KeyboardInterrupt |
| 100 | C3 RT2/RT3 a feature refusal is REFUSED (feature off), not HOLDS | `test_feature_refusals_are_refused_feature_not_holds`: AssertionError: 'HOLDS' != 'REFUSED (feature off; not a permission error)'; `test_rt2_feature_refusal_is_refused_feature_not_holds`: AssertionError: 'HOLDS' != 'REFUSED (feature off; not a permission error)' |
| 101 | C3 RT2 an auth or permission refusal without a positive control is INCONCLUSIVE | `test_rt2_auth_or_permission_refusal_has_no_positive_control`: AssertionError: 'HOLDS' != 'INCONCLUSIVE' |
| 102 | C3 RT3 an auth or permission refusal HOLDS only when B's own request succeeded | `test_rt3_refusal_without_a_successful_control_is_inconclusive`: AssertionError: 'HOLDS' != 'INCONCLUSIVE' |
| 103 | C3 RT3 the control, B's own identical request, is made | `test_rt3_auth_or_permission_refusal_holds_with_bs_own_request`: AssertionError: 'INCONCLUSIVE' != 'HOLDS' |
| 104 | C3 RT3 the matrix names B's session as RT3's control | `test_rt3_auth_or_permission_refusal_holds_with_bs_own_request`: AssertionError: 'INCONCLUSIVE' != 'HOLDS' |
| 105 | C3 RT3 the control's own events are not searched for the marker | `test_rt3_controls_own_events_are_not_searched`: AssertionError: 'FAIL' != 'HOLDS' |
| 106 | C3 F1 an observed FAIL survives a failed enabling request | `test_fail_survives_a_failed_enabling_request`: AssertionError: 'INCONCLUSIVE' != 'FAIL' |
| 107 | C3 F2 a restore's charge or limit signal is recorded | `test_a_signal_behind_another_stop_skips_the_cleanup`: AssertionError: Lists differ: ['/api/v2/chat/channels/delete', '/api/v2/users/delete'] != []; `test_a_signal_met_by_the_end_of_run_restore_skips_the_cleanup`: AssertionError: {'errors': [], 'channels_delete': 201, 'ch[407 chars]': 0} != {}; `test_rate_limited_restores_at_the_end_skip_the_cleanup`: AssertionError: {'errors': [], 'channels_delete': 201, 'ch[407 chars]': 0} != {} |
| 108 | C3 F2 finish() skips the cleanup after a recorded signal | `test_a_signal_behind_another_stop_skips_the_cleanup`: AssertionError: {'errors': ['not started: server PUT /api/[57 chars]ce']} != {}; `test_a_signal_met_by_the_end_of_run_restore_skips_the_cleanup`: AssertionError: {'errors': ['not started: server PUT /x: HTTP 402; stopping at once']} != {}; `test_a_signal_as_the_runs_own_stop_skips_the_cleanup`: AssertionError: {'errors': ['not started: client A: HTTP 402; stopping at once']} != {}; and 1 more |
| 109 | C3 F2 cmd_run adds its own stop to the run's record | `test_a_signal_as_the_runs_own_stop_skips_the_cleanup`: AssertionError: {'errors': [], 'channels_delete': 201, 'ch[407 chars]': 0} != {} |
| 110 | C3 F2 a signal met by the cleanup is recorded | `test_a_signal_met_during_cleanup_ends_it_and_is_recorded`: AssertionError: 0 != 1 |
| 111 | C3 F2 a signal ends the cleanup at once (untested until C3) | `test_a_signal_met_during_cleanup_ends_it_and_is_recorded`: AssertionError: 'users_delete' unexpectedly found in {'errors': ['channels: server POST /api/v2/chat/channels/delete: HTTP 429; stopping at once'], 'u… |
| 112 | C3 F2 a signal met by the final configuration read is recorded | `test_a_signal_met_by_the_final_configuration_read_is_recorded`: AssertionError: 0 != 1 |
| 113 | C3 F2 a rate limit is a charge or limit signal | `test_a_signal_met_during_cleanup_ends_it_and_is_recorded`: AssertionError: 'users_delete' unexpectedly found in {'errors': ['channels: server POST /api/v2/chat/channels/delete: HTTP 429; stopping at once'], 'u…; `test_rate_limited_restores_at_the_end_skip_the_cleanup`: AssertionError: {'errors': [], 'channels_delete': 201, 'ch[407 chars]': 0} != {} |
| 114 | C3 F2 the server's response hook marks and records a signal | `test_typed_and_raw_calls_mark_the_signal`: AssertionError: False is not true : 402 |
| 115 | C3 F2 the server's result check marks and records a signal | `test_the_result_check_marks_the_signal`: AssertionError: False is not true : 402 |
| 116 | C3 F2 a client's recorded request marks and records a signal | `test_every_client_signal_stops_at_once`: AssertionError: False is not true |
| 117 | C3 F2 a client's error marks and records a signal | `test_every_client_signal_stops_at_once`: AssertionError: False is not true |
| 118 | C3 review: the ledger records a signal as its stop is raised | `test_a_ctrl_c_that_replaces_the_stop_still_skips_the_cleanup`: AssertionError: Lists differ: [] != ['client A-role: HTTP 402; stopping at once']; `test_an_error_that_replaces_the_stop_still_stops_the_run`: AssertionError: RunStopped not raised; `test_a_signal_whose_stop_a_ctrl_c_replaced_skips_the_cleanup`: AssertionError: Lists differ: [] != ['client A-role: HTTP 402; stopping at once']; and 2 more |
| 119 | C3 review: a recorded signal stops the matrix after its case | `test_an_error_that_replaces_the_stop_still_stops_the_run`: AssertionError: RunStopped not raised |
| 120 | C3 nit 3 a pattern counts only at a line start | `test_a_pattern_matches_only_at_a_line_start`: AssertionError: Lists differ: [13] != []; `test_every_pattern_starts_a_line_once`: AssertionError: 2 != 1 : ('C2 nit 6 exactly one request', 'glow_stream_proof/proof_run.py') |
| 121 | C3 nit 3 an edited file that does not load is not demonstrated | `test_an_edit_that_does_not_compile_or_import_is_reported`: AssertionError: unexpectedly None : broken.py |
| 122 | C3 nit 4 a feature-on FAIL stays FAIL without a production answer | `test_feature_on_fail_survives_a_production_request_without_an_answer`: AssertionError: 'INCONCLUSIVE' != 'FAIL' |
| 123 | C3 nit 4 a polls-on FAIL stays FAIL without a production answer | `test_polls_on_fail_survives_a_production_vote_without_an_answer`: AssertionError: 'INCONCLUSIVE' != 'FAIL' |
| 124 | C3 nit 4 a guardrail met by the undo after an interruption stops the run | `test_a_guardrail_met_by_the_undo_after_an_interruption_stops_the_run`: AssertionError: GuardrailStop not raised |
| 125 | C3 nit 4 a second Ctrl-C keeps the problems finish() found | `test_second_ctrl_c_keeps_the_problems_finish_found`: AssertionError: 'temporary change not restored: still on' not found in ['the end of the run was interrupted (Ctrl-C): restores, cleanup and the config… |
| 126 | C3 nit 4 a second Ctrl-C closes the client processes | `test_second_ctrl_c_closes_the_client_sessions`: AssertionError: {'A': <tests.fakes.FakeSession object at 0[124 chars]890>} != {} |
| 127 | C3 nit 4 a client's error flags a rate limit | `test_the_error_only_check_flags_a_rate_limit`: AssertionError: False is not true |
| 128 | C3 nit 4 RT2/RT3 are INCONCLUSIVE unless B was listening | `test_a_refusal_while_b_is_not_listening_is_inconclusive`: AssertionError: 'HOLDS' != 'INCONCLUSIVE' |
| 129 | C3 nit 5 each request of a command is kept in the row | `test_each_request_of_a_command_is_kept_and_a_success_is_undone`: KeyError: 'requests' |
| 130 | C3 nit 5 a 2xx among a command's requests is undone | `test_each_request_of_a_command_is_kept_and_a_success_is_undone`: KeyError: 'client_success_undo' |
| 131 | C3 nit 6 B's probe stop is kept in the stops | `test_a_probe_stop_is_kept_and_its_signal_recorded`: AssertionError: "B's members query after AB's override removal: client B: HTTP 429; stopping at once" not found in ["restore failed: config_overrides … |
| 132 | C3 nit 6 B's probe stop is recorded as a signal | `test_a_probe_stop_is_kept_and_its_signal_recorded`: AssertionError: Lists differ: [] != ['client B: HTTP 429; stopping at once'] |
| 133 | C3 nit 7 no unset of A's member field after a guardrail stop | `test_no_unset_after_a_guardrail_stop_in_bs_reads`: AssertionError: Lists differ: [('PATCH', '/channels/glow-match/p061i1-si[44 chars]']})] != []; `test_no_unset_after_a_guardrail_stop_in_the_control`: AssertionError: 2 != 1 |
| 134 | C3 nit 8 a failed read of A's stored user stops the run | `test_e5`: AssertionError: RunStopped not raised; `test_s14`: AssertionError: RunStopped not raised |
| 135 | C3 nit 8 a listing without A stops the run too | `test_e5_is_inconclusive_when_as_stored_user_cannot_be_read`: AssertionError: RunStopped not raised; `test_s14_is_inconclusive_when_as_stored_user_cannot_be_read`: AssertionError: RunStopped not raised |
| 136 | C3 nit 9 the usage ledger is written through a temporary file | `test_an_interrupted_save_leaves_the_previous_ledger_whole`: json.decoder.JSONDecodeError: Expecting value: line 1 column 1 (char 0) |
| 137 | C3 nit 10 the early-write failure note is redacted | `test_the_early_write_failure_note_is_redacted`: AssertionError: 'RuntimeError: refused near <redacted-jwt> and <redacted-secret>' not found in 'results not written before the end of the run: Runtime… |
| 138 | C3 nit 8 a guardrail stop on the read of A's stored user is not deferred | `test_a_guardrail_stop_on_the_read_is_the_runs_stop`: glow_stream_proof.stops.RunStopped: after E5: E5: A's stored user could not be read: GuardrailStop: server GET /api/v2/users: HTTP 402; stopping at on… |
| 139 | C3 RT3 kept: both windows before the control | `test_rt3_marker_after_the_probe_survives_the_control_ending`: AssertionError: 'INCONCLUSIVE' != 'FAIL' |
| 140 | C3 F2 the client processes are closed when the cleanup is skipped | `test_a_signal_met_by_the_end_of_run_restore_skips_the_cleanup`: AssertionError: {'A': <tests.fakes.FakeSession object at 0[124 chars]7d0>} != {}; `test_rate_limited_restores_at_the_end_skip_the_cleanup`: AssertionError: {'A': <tests.fakes.FakeSession object at 0[124 chars]8c0>} != {}; `test_a_signal_as_the_runs_own_stop_skips_the_cleanup`: AssertionError: {'A': <tests.fakes.FakeSession object at 0[124 chars]7b0>} != {} |
| 141 | C3 nit 5 each case's row lists only its own commands | `test_each_request_of_a_command_is_kept_and_a_success_is_undone`: AssertionError: Lists differ: ['cli[39 chars]s/{m_a} -> 201, POST /messages/{m_a} -> 403', [83 chars]403'] != ['cli[39 chars]s/{m_b} -> 201, POST /mes… |
| 142 | C3 review: the production command's requests are listed in the row | `test_a_production_command_with_several_requests`: KeyError: 'requests' |
| 143 | C3 review: a 2xx among the production command's requests is undone | `test_a_production_command_with_several_requests`: AssertionError: 1 != 2 |
| 144 | C3 review: RT3's control counts only as the same request | `test_rt3_control_that_was_another_request_is_inconclusive`: AssertionError: 'HOLDS' != 'INCONCLUSIVE' |
| 145 | C3 review: S15 sends no unset after a recorded signal, whatever is in flight | `test_no_unset_after_a_signal_whose_stop_is_not_in_flight`: AssertionError: Lists differ: [('PATCH', '/channels/glow-match/p061i1-si[44 chars]']})] != [] |
| 146 | C3 review: no undo after a recorded signal, whatever is in flight | `test_no_undo_after_a_signal_whose_stop_an_error_replaced`: AssertionError: 'made after the interruption: undo POST 201' != "not made: a charge or limit signal was m[110 chars]nels" |
| 147 | C3 nit 5 a poll or group created among several requests is tracked | `test_a_poll_created_among_several_requests_is_deleted_at_cleanup`: AssertionError: 'client-poll' not found in [] |
| 148 | I2a guard: a user the run did not create is refused | `test_a_user_the_run_did_not_create_is_refused`: AssertionError: unexpectedly None : ('POST', '/api/v2/users/delete'); `test_a_refused_request_is_neither_sent_nor_counted`: AssertionError: GuardRefused not raised |
| 149 | I2a guard: a channel the run did not create is refused | `test_a_channel_the_run_did_not_create_is_refused`: AssertionError: unexpectedly None : ('DELETE', '/api/v2/chat/channels/messaging/someone-elses-channel'); `test_a_refusal_in_a_case_stops_the_run_after_its_row`: AssertionError: GuardRefused not raised |
| 150 | I2a guard: an application setting outside the journal is refused | `test_application_changes_outside_the_journal_are_refused`: AssertionError: unexpectedly None : ('PATCH', '/api/v2/app', {'revoke_tokens_issued_before': '2026-09-26T12:00:00Z'}); `test_the_run_is_the_guards_scope`: AssertionError: GuardRefused not raised |
| 151 | I2a guard: a match-type toggle outside the journal is refused | `test_match_type_changes_outside_the_journal_are_refused`: AssertionError: unexpectedly None |
| 152 | I2a guard: any other kind of change is refused | `test_other_kinds_of_change_are_refused`: AssertionError: unexpectedly None : /api/v2/chat/retention_policy |
| 153 | I2a guard: a message delete needs a message the run recorded | `test_a_message_poll_or_group_must_be_the_runs`: AssertionError: 'a message this run did not record' not found in 'None' |
| 154 | I2a guard: the server client asks the guard before sending | `test_a_refused_request_is_neither_sent_nor_counted`: AssertionError: GuardRefused not raised |
| 155 | I2a guard: the run installs the guard with itself as the scope | `test_the_run_is_the_guards_scope`: AssertionError: unexpectedly None; `test_a_refusal_in_a_case_stops_the_run_after_its_row`: AssertionError: GuardRefused not raised |
| 156 | I2a guard: cleanup --apply is guarded by the prefix | `test_cleanup_apply_is_guarded_by_the_prefix`: AssertionError: unexpectedly None |
| 157 | I2a guard: the deleted-user artifact the cleanup creates is recorded | `test_the_artifact_the_runs_cleanup_creates_may_be_deleted`: KeyError: 'artifact_users_delete' |
| 158 | I2a closing checks: verify compares every recorded setting | `test_an_application_wide_token_revocation_is_a_difference`: AssertionError: "revoke_tokens_issued_before is '2026-09-26T12:00:00Z', recorded None" not found in []; `test_every_hook_is_a_difference`: AssertionError: False is not true : webhook_url; `test_every_recorded_setting_is_compared_except_guest_creation`: AssertionError: "allow_multi_user_devices is 'changed', recorded False" not found in []; and 3 more |
| 159 | I2a closing checks: an unrecorded setting must be absent or empty | `test_a_setting_the_baseline_did_not_record_may_be_absent_or_empty`: AssertionError: 'channel_hide_members_only is True, recorded as absent' not found in []; `test_every_hook_is_a_difference`: AssertionError: False is not true : before_message_send_hook_url |
| 160 | I2a gap: the runner keeps a request sent outside a command | `test_every_request_is_reported_once_answered`: AssertionError: Lists differ: [('/late', 429)] != [('/between', 402), ('/late', 429)] |
| 161 | I2a gap: the runner keeps a command's request answered after its reply | `test_every_request_is_reported_once_answered`: AssertionError: Lists differ: [('/between', 402)] != [('/between', 402), ('/late', 429)] |
| 162 | I2a gap: a reply's requests outside its command are checked | `test_a_request_sent_between_commands`: AssertionError: GuardrailStop not raised; `test_an_answer_that_came_after_its_command_replied`: AssertionError: GuardrailStop not raised; `test_an_asynchronous_sdk_error`: AssertionError: GuardrailStop not raised |
| 163 | I2a gap: an asynchronous SDK error is checked | `test_an_asynchronous_sdk_error`: AssertionError: GuardrailStop not raised; `test_the_end_of_the_run_closes_without_raising`: AssertionError: 0 != 1 |
| 164 | I2a gap: the runner's own refusal is not a signal | `test_a_request_the_runner_refused_is_not_a_signal`: glow_stream_proof.usage.GuardrailStop: client fake: response text mentions a charge, upgrade or exceeded limit (an asynchronous SDK error); stopping a… |
| 165 | I2a gap: calls sent between commands are counted | `test_a_request_sent_between_commands`: AssertionError: 0 != 1 |
| 166 | I2a gap: closing a session checks its exit reply | `test_a_signal_at_exit_is_raised_when_nothing_else_is_in_flight`: AssertionError: GuardrailStop not raised; `test_a_signal_at_exit_never_replaces_an_exception_in_flight`: AssertionError: 0 != 1; `test_the_end_of_the_run_closes_without_raising`: AssertionError: 0 != 1 |
| 167 | I2a gap: a signal at exit is raised only when nothing else is in flight | `test_a_signal_at_exit_never_replaces_an_exception_in_flight`: glow_stream_proof.usage.GuardrailStop: client fake: HTTP 402 (a request sent between commands); stopping at once |
| 168 | I2a gap: the end of the run closes its sessions without raising | `test_a_signal_a_session_reports_as_it_closes_skips_the_cleanup`: glow_stream_proof.usage.GuardrailStop: client A: HTTP 402 (a request sent between commands); stopping at once |
| 169 | I2a gap: the sessions close before the cleanup is decided | `test_a_signal_a_session_reports_as_it_closes_skips_the_cleanup`: AssertionError: 0 != 1 |
| 170 | I2a gap: the cleanup checks again once the sessions are closed | `test_the_cleanup_checks_again_once_the_sessions_are_closed`: AssertionError: Lists differ: ['/api/v2/chat/channels/delete', '/api/v2/users/delete'] != [] |
| 171 | I2a nit 1: RT3's control window is searched | `test_rt3_control_window_is_searched_but_for_bs_own_read_events`: AssertionError: 'HOLDS' != 'FAIL' |
| 172 | I2a nit 1: only read events are left out of the control window | `test_rt3_control_window_is_searched_but_for_bs_own_read_events`: AssertionError: 'HOLDS' != 'FAIL' |
| 173 | I2a nit 1: only the control member's own read events are left out | `test_rt3_control_window_is_searched_but_for_bs_own_read_events`: AssertionError: 'HOLDS' != 'FAIL' |
| 174 | I2a nit 2(a): a charge signal met by the cleanup ends it (402 and code 99) | `test_a_charge_signal_met_during_cleanup_ends_it_too`: AssertionError: 'users_delete' unexpectedly found in {'errors': ['channels: server POST /api/v2/chat/channels/delete: HTTP 402; stopping at once'], 'u… |
| 175 | I2a nit 2(b): S15 sends no unset after a budget stop | `test_no_unset_after_a_budget_stop_in_bs_reads`: AssertionError: Lists differ: [('PATCH', '/channels/glow-match/p061i1-si[44 chars]']})] != [] |
| 176 | I2a nit 2(c): RT3's control only after an authentication or permission refusal | `test_rt3_control_is_sent_only_after_an_auth_or_permission_refusal`: AssertionError: Lists differ: [{'max_calls': 2, 'target': 'channel', 'me[155 chars]'}]}] != [] |
| 177 | I2a nit 4: a phase's undo note is kept beside the earlier one | `test_both_phases_undo_notes_are_kept`: AssertionError: 'production: undo DELETE 200' != 'undo DELETE 200; production: undo DELETE 200' |
| 178 | I2a nit 5: the printed report lists the charge or limit signals | `test_the_report_lists_every_charge_or_limit_signal`: AssertionError: 'Charge or limit signals:\n- server GET /x: HTTP 429; stopping at once' not found in 'Run `p061i1-x`\n\nAuthorized path\n\n\| Check \|… |
| 179 | I2a DM-04 9(c): the cleanup's prefix scan includes deactivated users | `test_a_deactivated_user_with_the_prefix_is_found_and_deleted`: AssertionError: 0 != 1 |
| 180 | I2a signals by kind: only a rate limit without billing wording is only a rate limit | `test_anything_else_is_a_charge_signal`: AssertionError: 'only a rate limit: wait at least 60 s (or[94 chars]run)' != 'a charge signal: make no further live call, and report it' |
| 181 | I2a signals by kind: billing wording in the server's response hook | `test_a_rate_limit_with_quota_wording_is_a_charge_signal`: AssertionError: False is not true |
| 182 | I2a signals by kind: billing wording in the server's result check | `test_a_rate_limit_with_quota_wording_is_a_charge_signal`: AssertionError: False is not true |
| 183 | I2a signals by kind: billing wording in a client's recorded request | `test_record_and_error_sites`: AssertionError: False is not true |
| 184 | I2a signals by kind: billing wording in a client's error | `test_record_and_error_sites`: AssertionError: False is not true |
| 185 | I2a signals by kind: billing wording in an asynchronous SDK error | `test_an_asynchronous_sdk_error`: AssertionError: False is not true |
| 186 | I2a signals by kind: a rate limit's stop names its reset | `test_the_stop_names_the_reset`: AssertionError: 'HTTP 429 (x-ratelimit-reset 1790309999); stopping at once' not found in 'server POST /api/v2/users: HTTP 429; stopping at once' |
| 187 | I2a review 3: every signal in a reply is recorded | `test_a_charge_behind_a_rate_limit_is_recorded`: AssertionError: 1 != 2 |
| 188 | I2a review 3: a signal is recorded before the calls are counted | `test_a_signal_is_not_hidden_by_the_budget`: AssertionError: False is not true |
| 189 | I2a step 2 guard: a member named in the path | `test_a_user_the_run_did_not_create_is_refused`: AssertionError: unexpectedly None : ('PATCH', '/channels/glow-match/p061i1-0926000000-ch-ab/member/dashboard-owner-7f3a') |
| 190 | I2a step 2 outage: the app send path refuses an unreachable provider | `test_an_unreachable_provider_refuses_the_send_and_keeps_nothing`: glow_stream_proof.app_send.ProviderUnavailable: ConnectError: injected outage; `test_the_send_is_refused_and_nothing_is_kept`: AssertionError: 'FAIL' != 'HOLDS' |
| 191 | I2a step 2 outage: the server send turns a connection error into a refusal | `test_the_send_is_refused_and_nothing_is_kept`: AssertionError: 'FAIL' != 'HOLDS' |
| 192 | I2a step 2 delete: the hard-deleted user is not named at cleanup | `test_deactivation_and_the_hard_delete`: AssertionError: 'p061i1-simulated-uh' unexpectedly found in ['p061i1-simulated-ua', 'p061i1-simulated-ub', 'p061i1-simulated-ux', 'p061i1-simulated-ud… |
| 193 | I2a step 2 delete: the channel the delete removed is not named at cleanup | `test_deactivation_and_the_hard_delete`: AssertionError: 'glow-match:p061i1-simulated-ch-delete' unexpectedly found in ['glow-match:p061i1-simulated-ch-ab', 'glow-match:p061i1-simulated-ch-xd… |
| 194 | I2a step 2 sessions: the I1 sessions close before the families | `test_the_i1_sessions_close_before_the_families_only_when_one_runs`: AssertionError: 'A' unexpectedly found in {'A': <tests.fakes.FakeSession object at 0x7fc563050c80>, 'B': <tests.fakes.FakeSession object at 0x7fc56305… |
| 195 | I2a step 2 sessions: a family closes its own sessions | `test_a_familys_own_sessions_are_closed_at_its_end`: AssertionError: Items in the first set but not the second: |
| 196 | I2a step 2 budget: a case starts only with the calls it declared | `test_a_family_starts_only_with_the_calls_it_declared`: AssertionError: Lists differ: ['R1', 'RV-remove'] != ['R1'] |
| 197 | I2a step 2 rules: a revocation dimension needs a successful control | `test_a_dimension_ends_only_on_an_attributable_refusal_after_a_control`: AssertionError: 'ended' != 'not shown' |
| 198 | I2a step 2 rules: an ended subscription needs a listener that received the probe | `test_the_subscription_ends_only_with_a_listener_that_received_it`: AssertionError: 'ended' != 'not shown' |
| 199 | I2a step 2 oracle: a channel a probe created is counted | `test_a_missing_channel_that_a_probe_created_is_counted_and_cleaned_up`: AssertionError: 2 != 3 |
| 200 | I2a step 2 S15 mapping: a member field not restored stops the run | `test_a_restore_that_fails_stops_the_run_after_the_case`: AssertionError: RunStopped not raised |
| 201 | I2a review 1: a write is put back however the field ends | `test_a_field_the_control_set_is_restored_when_bs_session_ends`: AssertionError: 'channel_moderator' != 'channel_member' |
| 202 | I2a review 1: nothing is put back for a field that reads as it was | `test_nothing_is_put_back_for_a_field_that_was_never_changed`: AssertionError: 13 != 2 |
| 203 | I2a review 1: nothing is sent to restore after a guardrail stop | `test_nothing_is_sent_to_restore_after_a_guardrail_stop`: AssertionError: Lists differ: [{'unset': ['glow_note']}] != [] |
| 204 | I2a review 1: a record that cannot be read after the restore stops the run | `test_a_record_that_cannot_be_read_after_restoring_stops_the_run`: AssertionError: False is not true |
| 205 | I2a review 2: the listeners are collected first | `test_a_late_delivery_is_not_taken_for_an_ended_subscription`: AssertionError: Lists differ: ['M1', 'M2'] != ['M2', 'M1'] |
| 206 | I2a review 2: a member that missed the probe gets a second window | `test_a_late_delivery_is_not_taken_for_an_ended_subscription`: AssertionError: False is not true |
| 207 | I2a review 2: a closed or recovered connection leaves a miss not shown | `test_the_subscription_ends_only_with_a_listener_that_received_it`: AssertionError: 'ended' != 'not shown'; `test_a_closed_or_recovered_connection_leaves_a_channel_level_miss_not_shown`: AssertionError: 'ended' != 'not shown' |
| 208 | I2a review 2: an account-level mechanism's close is not taken for a drop | `test_an_account_level_close_may_end_the_subscription_a_recovery_may_not`: AssertionError: 'not shown' != 'ended' |
| 209 | I2a review 2: the mechanism's own window counts | `test_a_close_in_the_mechanisms_own_window_counts_too`: AssertionError: 'ended' != 'not shown' |
| 210 | I2a review 4: an account-level mechanism is judged on a token issued after it | `test_token_revocation_on_two_devices`: KeyError: 'token_issued_after' |
| 211 | I2a review 4: the revocation's late token is the token issued after it | `test_token_revocation_on_two_devices`: AssertionError: 'not shown' != 'not ended' |
| 212 | I2a review 4: deactivation and deletion issue a token after the mechanism | `test_deactivation_and_the_hard_delete`: AssertionError: 'INCONCLUSIVE' != 'MEETS the history policy' |
| 213 | I2a review 4: the policy requires every dimension of the mechanism | `test_the_policy_requires_every_dimension_of_the_mechanism`: AssertionError: 'MEETS the history policy' != 'INCONCLUSIVE' |
| 214 | I2a review nit: a connect after the hard delete names the user at cleanup again | `test_a_connect_that_creates_the_deleted_user_again_is_cleaned_up`: AssertionError: 'p061i1-simulated-uh' not found in ['p061i1-simulated-ua', 'p061i1-simulated-ub', 'p061i1-simulated-ux', 'p061i1-simulated-ud', 'p061i… |
| 215 | I2a review 6: a pair without a determinate answer is inconclusive | `test_a_pair_without_an_answer_is_inconclusive`: AssertionError: 'not attributable' not found in 'getMessage: identical no-response errors (no answer recorded (error: local SDK error)): the request m… |
| 216 | I2a review 6: identical input or feature errors show nothing | `test_identical_input_errors_are_inconclusive`: AssertionError: 'HOLDS' != 'INCONCLUSIVE' |
| 217 | I2a review 7: an oracle seen before an interruption stays a FAIL | `test_an_oracle_seen_before_an_interruption_stays_a_fail`: AssertionError: 'INCONCLUSIVE' != 'FAIL' |
| 218 | I2a review 8: the delete's channel is checked at cleanup before the delete is sent | `test_a_stop_during_the_hard_deletes_task_leaves_the_channel_checked_first`: AssertionError: 'glow-match:p061i1-simulated-ch-delete' not found in set(); `test_the_cleanup_names_no_user_or_channel_that_is_gone`: AssertionError: 'glow-match:p061i1-simulated-ch-delete' not found in set() |
| 219 | I2a review nit: the guard reads a mute's target | `test_a_user_the_run_did_not_create_is_refused`: AssertionError: unexpectedly None : ('POST', '/api/v2/moderation/mute') |
| 220 | I2a review nit: the guard reads a poll update's poll from its body | `test_a_message_poll_or_group_must_be_the_runs`: AssertionError: 'a poll this run did not record' not found in 'None' |
| 221 | I2a review nit: a show is sent only once the channel is hidden again | `test_a_hide_that_is_not_made_again_leaves_the_undo_unjudged`: AssertionError: False is not true |
| 222 | I2a review nit: a delete whose task did not complete is not judged | `test_the_cleanup_names_no_user_or_channel_that_is_gone`: AssertionError: 'MEETS the history policy' != 'INCONCLUSIVE' |
| 223 | I2a review nit: expiry controls count only well before the expiry | `test_controls_that_finish_too_close_to_the_expiry_are_inconclusive`: AssertionError: 'HOLDS' != 'INCONCLUSIVE' |
| 224 | I2a review nit: G2's guest creation is tried again after any refusal | `test_any_refusal_is_tried_again_with_guest_creation_enabled`: KeyError: 'with_guest_creation_enabled' |
| 225 | I2a review nit: the run plan counts what the session already used | `test_what_the_session_already_used_is_counted`: AssertionError: True is not false |
| 226 | I2a review nit: a case runs only while the setup tokens are far from expiry | `test_a_case_is_not_run_while_the_setup_tokens_are_close_to_expiry`: AssertionError: 'HOLDS' != 'INCONCLUSIVE' |
| 227 | I2a review nit: the reconnect check is not made near the tokens' expiry | `test_a_case_is_not_run_while_the_setup_tokens_are_close_to_expiry`: AssertionError: 'not made' not found in 'disconnect ok; reconnect ok (succeeded); watch 403 / code 17; message.new received True' |
| 228 | I2a review nit: a family runs only while the shared tokens are far from expiry | `test_a_family_is_not_run_while_the_shared_tokens_are_close_to_expiry`: AssertionError: 'DOES NOT MEET the history policy' != 'INCONCLUSIVE' |
| 229 | I2a review nit: no refusal near the member's own expiry is an ended dimension | `test_a_refusal_near_the_members_own_expiry_is_not_an_ended_dimension`: AssertionError: 'MEETS the history policy' != 'INCONCLUSIVE' |
| 230 | I2a live: a listing not verified keeps Stream's message | `test_verify_clean_lists_polls_and_user_groups`: AssertionError: 'remaining_user_groups: not verified: HTTP 400 code 4: not supported' not found in ["remaining_polls: ['left-poll']", 'remaining_user_… |
| 231 | I2a live: a channel's ID never replaces the command's own ID | `test_a_channel_command_keeps_its_own_id_end_to_end`: glow_stream_proof.client_bridge.ClientSessionEnded: client t ended: reply id 'proof-channel' does not match command id 2 |
| 232 | I2a live: the runner opens the channel named by channel_id | `test_a_channel_command_names_its_channel_as_channel_id`: AssertionError: 'glow-match:proof-channel' not found in "Channel glow-match:2 hasn't been initialized yet. Make sure to call .watch() and wait for it …; `test_a_channel_command_keeps_its_own_id_end_to_end`: AssertionError: 'glow-match:proof-channel' not found in "Channel glow-match:2 hasn't been initialized yet. Make sure to call .watch() and wait for it … |
| 233 | I2a review 7: a family goes on when a member's session has ended | `test_an_ended_client_session_ends_only_its_case`: AssertionError: 'after_probe' not found in {'mechanism': 'remove', 'scope': 'channel', 'setup': {'channel': '{CH_remove}', 'connected': {'M1': 'ok (su… |
| 234 | I2a review 7: a session that ends at the S15 write leaves that dimension not shown | `test_an_ended_client_session_ends_only_its_case`: KeyError: 'M1' |
| 235 | I2a review 7: an interrupted family keeps DOES NOT MEET | `test_an_interrupted_family_keeps_what_does_not_meet_the_policy`: AssertionError: 'INCONCLUSIVE' != 'DOES NOT MEET the history policy' |
| 236 | I2a review 7: a family's row is kept after each step | `test_an_interrupted_family_keeps_what_does_not_meet_the_policy`: AssertionError: 'INCONCLUSIVE' != 'DOES NOT MEET the history policy'; `test_a_rate_limit_in_a_probe_keeps_what_was_observed`: AssertionError: 'M1: rest ended' not found in 'applied: 201' |
| 237 | I2a review 7: an interrupted S15 mapping keeps the field in progress | `test_a_field_the_control_set_is_restored_when_bs_session_ends`: KeyError: 'interrupted' |
| 238 | I2a review 7: an interrupted pin or archive keeps the restore's note | `test_a_leak_stays_a_fail_when_the_control_is_interrupted`: AttributeError: 'NoneType' object has no attribute 'endswith' |
| 239 | I2a review 5: HOLDS (filtered) needs B's read to return A's member record | `test_a_b_read_without_as_member_record_is_inconclusive`: AssertionError: 'HOLDS (filtered, not refused)' != 'INCONCLUSIVE'; `test_a_refused_b_read_is_inconclusive`: AssertionError: 'HOLDS (filtered, not refused)' != 'INCONCLUSIVE' |
| 240 | I2a review 5: HOLDS needs a readable stored record | `test_a_stored_record_that_cannot_be_read_is_inconclusive`: AssertionError: 'HOLDS (accepted, not applied)' != 'INCONCLUSIVE' |
| 241 | I2a step 2 S10: the poll message is sent again until polls reach the channel | `test_the_poll_message_is_retried_until_polls_reach_the_channel`: AssertionError: 1 != 3 |
| 242 | I2a step 2 G2: the guest is created server-side | `test_guest_reach_runs_on_a_guest_created_server_side`: AssertionError: unexpectedly None : G2's server-side setup was not made |

### Deviations and limits

- **Run 1 was spent by a harness defect** (C1's reply matching with a channel command), before any case; the one reserve rerun then ran every case. No run remains in this session: a case family that needs a rerun waits for I2b.
- **The poll listing is not verified** in any run or check: server-side Query Polls needs a user, and the proof never uses the dashboard user. Nothing points to a leftover poll (earlier runs deleted theirs, and both runs deleted theirs by recorded ID with 200), but none can be shown absent. Both runs exited 4 for it, and `verify-clean` exited 1.
- **Two FAILs read otherwise** (F9-thread and F9-sync): their only "disclosed" term was one A's own request carried. Recorded as FAIL; the rule is for the manager to decide.
- **EO-channel's `query` and `watch` pairs** were judged different on Stream's message text, which the row does not keep; their FAIL rests on the harness's comparison alone. The `GET` pair's FAIL stands on status and code.
- **The interpretation the prompt asks me to flag:** the four channel-level mechanisms share M1 and M2, each on a separate channel of its own (revision 1 of the prompt: "Channel-scoped mechanisms can share users on separate channels; user-scoped ones … need their own users"; DM-04 finding 5's count basis). Each family's controls show that no earlier family had reached its channel (M1's reads, writes and subscription succeeded before each channel-level mechanism).
- **Deactivation's 404 code 16** (Stream's "does not exist" for a deactivated user) is not counted as an ended dimension, because the rule counts only authentication and permission errors; SD-deactivate is INCONCLUSIVE though S was locked out in every request made.
- **Not exercised live:** every charge-signal path (none came), the rate-limit retry, the interruption paths (no case was interrupted in run 2), the stop paths of step 1, RT3's control, and `restore --apply`.
- **The fakes do not model the client protocol:** they replace `ClientSession`, so the channel-command defect was invisible offline; two tests now drive the real runner offline for it.
- **Sub-agents:** a read-only sub-agent made the independent check (its report was taken in full; I verified every finding in the code or by reproduction before fixing it). Two read-only research sub-agents read Stream's documentation (getstream.io only). None made a Stream call.
- **Timing:** the families' observations used 2.5 s event windows (a second window when a member missed the probe) and a 7 s wait for the revocation; slower deliveries than that are not ruled out.

### What I2b and P06.2 must know

- **Findings for the product (P06.2):**
  - No Stream mechanism meets the history policy on its own. Removal comes closest (it ends reads, the open subscription and token reuse; the member's own write then gets 404). A channel ban, hide and freeze leave the member reading the conversation and its events; hide is undone by the member's own client. Per-user revocation ends every existing token and subscription, but a token issued after it works, so the app's token endpoint must refuse the user. Deactivation locks the user out with 404 code 16 and keeps the data. The hard delete removes the conversation, the history the policy keeps for safety reports, and the user's old token, or a new one, can connect afterwards; that the connect re-creates the user is inferred from its success, not shown by a read of the user (corrected in P06.1-I2b; the I2a review's nit 6).
  - Free-text paths to the other member outside the app's send path: invite accept and reject with a message (stored, and delivered as `message.new` and `channel.updated`); AI-indicator events (`updateAIState` with `ai_message`), accepted with custom events off; member custom data (S15) and a member's own `pinned` and `archived` flags, visible to the other member; and a member's write to the other member's membership was accepted (200).
  - Existence oracles: Get Channel (403 or 404) and `getMessage` (403 or 404) tell a non-member whether a channel or message ID exists; error messages of `getReplies` and `getReactions` name the channel of a message ID.
  - An open WebSocket connection outlived its token's expiry (TD-expiry), while REST and reconnection were refused.
- **For the harness (I2b):**
  - Decide the disclosure rule: whether a term the request itself carried counts (F9-thread, F9-sync). If not, exclude such terms and keep the response's key names in the row.
  - Keep the two normalized messages in each existence-oracle pair, so a FAIL on text can be read.
  - Fix the poll listing: server-side Query Polls needs `user` or `user_id`; whether that narrows the listing to that user's polls is not documented and needs a read of the API reference or a probe with the run's own user.
  - Decide whether a deactivated user's 404 code 16 counts as ended.
  - Stream's code-43 message quotes the application's API key; the redactor does not remove the API key from free text. It is not the secret, but records may prefer it removed.
  - The fakes replace `ClientSession`; a test that drives the real runner (offline) is the only guard on the client protocol.
- **Session state:** the ledger (this checkout's `.work/usage-ledger.json`) holds 15 users, 20 channels and 698 calls; a new session starts from zero. The application holds no proof data, one other user (the dashboard user) and the configuration verifies ("differences before: []").

### Manager verification of I2a (App Manager 3, 26 September 2026)

App Manager 3 checked the relayed report against the pushed branch. The manager makes no call to Stream. The live results therefore rest on this record and on the code that produced them, and I2a's exact-head review checks both.

- **Identity:**
  - branch `claude/p06-1-i2a-revocation-safety-wms9ea`, head `761fa289f1dacd13b8d48b78db6b220d07c079e3`, tree `f23c04c735a5de3442bca742828e2c1b9cbc0bf6`; step 1 `f3ef40b`; code head `7ce93cc`; run 1 from `5df522c`;
  - nine commits on the start `6e67fd6`: 41 files, +9,442 and −246. The last commit changes only this record;
  - every path is owned: 40 under `proofs/stream-chat/`, 12 of them new, and this record. All 64 files under `proofs/stream-chat/` have mode 100644. No dependency file, lock, `.npmrc`, `pyproject.toml` or the committed baseline changed, and `git diff --check` is clean;
  - the eight sections the I2a prompt protects are byte-identical to the start. The two in-place "(corrected in P06.1-I2a)" markers are in C1's own section, in the rows of finding 5 and nit 13.
- **Each live run from a pushed commit.** The branch's push runs show when each commit reached GitHub: `651c2df` at 21:03 UTC, `5df522c` at 21:08 and `7ce93cc` at 21:32. Each was pushed before the live commands this record ties to it: the checks at 21:05, the checks at 21:25 and run 1 at 21:26, and run 2 at 21:50. The push runs on the two run heads passed: [36271890104](https://github.com/amthorn78/glow-dating-app/actions/runs/36271890104) (`5df522c`) and [36273299781](https://github.com/amthorn78/glow-dating-app/actions/runs/36273299781) (`7ce93cc`).
- **Classification:** the trusted policy from `main` (`0f45e64`), run outside the tree with `python3 -I`, gave full scope (`behavior-or-empty`) for 41 paths, with one merge base.
- **Offline re-run,** in a scratch export of `7ce93cc`, in clean processes without any `STREAM_*` variable. Installs got the proxy and CA variables by reference.
  - `pip install --require-hashes -r requirements-dev.lock`, then `pip check`: "No broken requirements found." `getstream` 6.1.0, Ruff 0.16.8, mypy 2.3.1.
  - `npm ci --ignore-scripts`, with the pinned npm 11.9.0: "found 0 vulnerabilities"; `stream-chat` 9.53.0; the lock unchanged.
  - Unit tests: `Ran 393 tests`, `OK`. Ruff check: "All checks passed!". Ruff format: "51 files already formatted". mypy: "Success: no issues found in 49 source files". `node --check` on the three `.cjs` files: exit 0.
  - `checks/fix_reversals.py`: "reversals: 242, not demonstrated: 0", exit 0, in 13 minutes. The manager read each failure reason, as AM3-18 requires: 206 reversals failed on an assertion and 33 on the error their reverted fix causes (a missing key, the injected stop, a torn write, the live message of the run-1 defect), and three aborted through a Ctrl-C by design. None failed through a syntax, import or name error, and the export was unchanged afterwards.
- **Secret scan** of the whole diff to the head (666,258 bytes): no JWT-shaped string, email address, private-key block, AWS-style, GitHub or Slack token, TLS-weakening setting, environment dump or secret assignment, and no copy of the development application's API key.
  - **The API key in four tracked files.** The session's notes, relayed with its report, say the key "was already present in those four tracked files beforehand". They are the documents that record it as a client-safe identifier, not a credential: `docs/continuity/claude-code-handoff.md` ("Client-safe identifier; not sufficient to authenticate a user"), the environment inventory, the P06.1 brief and the archived M02 handoff. I2a changed none of them. The key's only other appearance is inside Stream's own code-43 message, in the session's local `.work` results, which are not committed.
- **Code read,** at `7ce93cc`:
  - the run-1 fix (`client_bridge.py` `send`; `client/runner.cjs`): a command's `id` parameter now travels as `channel_id`, and the command's own `id` is set last. The runner reads `cmd.id` only in its replies. Its `call` op opens the channel from `channel_id`, and its `get` op takes the path the Python side built;
  - the guard's stated scope (`guard.py`) and its call from the server client's request hook (`server_api.py`, `_before_request`), before a request is counted or sent.
- **The record's counts:** run 2's verdicts add up to its 114 cases (82, 5, 3, 1, 13, 4, 5 and 1).
- **Integration:** merged into the manager branch as `6a51dae3e0f2b7a69097151fb5e5dcfe4414b61d`, pushed alone at 23:05 UTC. Against its first parent, the merge brings exactly I2a's 41 files. Against I2a's head, it differs only in the manager's records of `b581e42`, `edba0e6` and `82d0dd4`.
- **Hosted CI on `6a51dae`:** push run [36278363805](https://github.com/amthorn78/glow-dating-app/actions/runs/36278363805) passed all six jobs, and its gate says `Application checks passed`. The rendered suite passed 84 of 84 on the pinned Chromium in 3.3 minutes. PR run [36278366585](https://github.com/amthorn78/glow-dating-app/actions/runs/36278366585): passed all six jobs too, and its gate says `Application checks passed`. No Foundation job runs the harness's own tests yet (I2b adds one); the offline re-run above covers them.

#### The decisions I2a left to the manager

The first two are proposed rules for I2b's runs. The exact-head review assesses them before they take effect, and I2b's prompt fixes them. Every recorded verdict stands as recorded.

- **The disclosure rule (F9-thread and F9-sync).** A term that the request itself carried tells the sender nothing new.
  - **Proposed rule:** the disclosure scan leaves out terms present in the request's path, query or body, and the row keeps the key names of the response where a term was found.
  - **Under it:** F9-thread shows nothing either way, because A and X got the same 404 code 16. F9-sync returned none of XD's content. Whether `sync` answers differently for an existing and a missing channel was not tested, so I2b adds a `sync` pair to the existence oracle.
- **404 code 16 as "ended"** (SD-deactivate, and M1's own member write after RV-remove). The matrix quality rule counts only authentication and permission errors, because a 404 can have other causes.
  - **Proposed rule:** a 404 code 16 counts as ended only when all three hold: the same request by the same member succeeded before the mechanism; the mechanism removed or disabled what the request needs (the membership after a removal, the user after a deactivation); and Stream's message, kept in the row, says so. Otherwise it stays "not shown".
  - **Under it:** deactivation would end S's access; its server-side send's message names the deactivation. That is account-wide, not per conversation. Removal would meet the history policy for the removed member if the message of M1's own write confirms the missing membership; run 2 did not keep that message.
  - **Nothing is claimed yet.** I2b reruns RV-remove and SD-deactivate live under the rule, keeping the messages, and I2b's review confirms the result.
- **The poll listing.** Server-side Query Polls needs a user, and the proof never uses the dashboard user. I2b reads Stream's API reference for Query Polls. It then either lists polls as each of the run's own users before that user is deleted, or confirms each recorded poll gone by ID. Until one of those shows the polls absent, "not verified" stays in the record and is reported. On its own, it does not stop a run.

**Accepted as done:**

- **`verify-clean` exited 1 before each run,** for the poll listing alone, and the session went on. The prompt expected "no … polls" and said to report anything the harness marks "not verified". Nothing showed a poll, and each run deleted its own polls by recorded ID. I2b's prompt will say that a poll listing "not verified" does not stop a run.
- **The reserve rerun named all 114 cases.** Run 1 completed none, and the prompt's reserve is "for cases run 1 could not complete", within what the session has left. It fitted: 15 of 20 users and 20 of 30 channels.
- **M1 and M2 were shared by the four channel-level mechanisms, each on a channel of its own.** The prompt forbids sharing "to meet a number". The count fitted with room to spare, DM-04's own estimate assumed this sharing, and each family's controls show that no earlier mechanism had reached the next channel. DM-04's summary table put the condition more strictly ("no sharing of users or channels between mechanisms"), so the manager puts this reading to the Dev Manager with I2b's prompt.

#### Disposition

- **I2a is verified and integrated** at `6a51dae3e0f2b7a69097151fb5e5dcfe4414b61d`. Its product findings are recorded under "What I2b and P06.2 must know". A design decision that rests on one of them stays conditional until a review confirms it live (DM-01 P4); for removal, that is I2b's rerun and I2b's review.
- **I2b also carries:** the two rules above once assessed; the existence oracle keeping both normalized messages of each pair; the poll listing; removing the API key from free text in outputs; and the live reruns of RV-remove and SD-deactivate.
- **I2a's exact-head review is next,** offline and scoped to I2a's change. After it, only certain findings delay I2b: a blocking finding, or a should-fix finding that could create a false HOLDS or a false "ended", lose an observed FAIL or DOES NOT MEET, send a request after a charge or limit signal, or let a change escape the guard. Other findings go into I2b's offline first step.

### Exact-head review of I2a (27 September 2026)

Nathan ran the review session at extra high, from revision 1 of the [review prompt](../../ephemeral/2026-09-26-p06-1-i2a-review-prompt.md) (records commit `9fc3b50`), and relayed its report. The session committed and pushed nothing, and made no Stream call.

- **Verdict: approve.** I2a's harness and record are a sound base for I2b's live runs. The C3 review's items, DM-04's conditions and the independent check's findings are confirmed fixed. The product findings are sound, but the hard delete's re-creation of the user is an inference (nit 6). The reviewer agrees with the manager's decisions, with one detail for the disclosure rule and one refinement for 404 code 16.
- **Two should-fix findings and four nits remain, and no recorded result changes.** Finding 1 falls, narrowly, in a class that delays I2b's live runs: an interruption inside a family step loses that step's observations, so a DOES NOT MEET could be recorded as INCONCLUSIVE, never as a pass. Finding 2 can give the existence oracle a false FAIL.

#### The report, as relayed

The session's notes before its report, verbatim:

> I'll begin with the environment check (names only) and the start gate, then read the required documents and diff before running the offline checks.
>
> Environment check passes: none of the six variable names is present, and the toolchain matches expectations. Now the start gate.
>
> All start-gate checks pass. Now the three classifications, the diff whitespace check, and file mode checks.
>
> All three classifications match expectations. Now the whitespace check, file modes, symlinks, and a first look at the diff's shape.
>
> Start gate and scope checks are clean. Now the reading. I'll begin with the I2a prompt, DM-04 and its disposition, then the harness README and the evidence record.
>
> I'm reading the governing documents in full before the code. The README is large, so I'll read it in two parts, and pull the evidence record's section map in parallel.
>
> I've reviewed the README. Next I'll pull the evidence record's structure, C3 review, the "must know" lists, I2a's section, corrections, and the brief/manager verification at `9fc3b50`—while kicking off the installs in the background to run in parallel.
>
> I'm checking that the install directories are git-ignored before I install, and reading the evidence record's sections in parallel.
>
> I'll continue reading I2a's evidence, then pull the remaining independent pieces together: the rest of that section, the brief and manager verification at the later commit, and the install log.
>
> Installs completed cleanly. I'll kick off the offline checks and fix-reversal run in the background (about 20 minutes), and meanwhile read through I2a's section, the brief, and the manager's verification at the later commit.
>
> I've finished reviewing the governing documents and records. Next, I'll read the new modules (guard, stops, request log, run plan) and the server client's hook in parallel, followed by the larger I2a and mechanisms modules.
>
> I've reviewed the guard, client bridge, mechanisms, and I2a modules. Next I'll check the case loop, end-of-run code, cleanup command, guard/real-runner tests, SDK client wiring, and runner command fields.
>
> Two earlier commands failed since they ran in the wrong directory, so I'll rerun them with absolute paths, then check the SDK's retry/exception handling, runner command fields, fakes, protected-section comparison, secret scan, and reversal-log progress.
>
> I'll now run several checks in parallel: re-check the C1 section diff, verify the reversal run's status, examine the fix-reversal table structure to review I2a's 95 entries, set up a mutation harness to test the key fixes, and locate where the API key is recorded to scan the diff for it.
>
> I'll write the missing mutation harness file and kick off its run, while the reversal run continues (169/242). Meanwhile, I'll check the baseline's recorded settings against the closing-check code.
>
> Mutations M1-M4 were caught, but M5 survived since the token-margin test only covers one dimension—I'll note this as a test-gap issue. While remaining runs finish, I'll check two things against the fakes: whether an interruption mid-family-step loses a "not ended" observation, and whether the oracle's size comparison is sensitive to Stream's variable-length `duration` field.
>
> Both probes confirm that a stop inside a family step drops the member's "not ended" read, causing the oracle's size comparison to misread a duration difference as a FAIL. Now I'll gather the reversal and mutation results.
>
> The reversal run is alive and near its end (it's on reversal 222 of 242), and the mutations are at 17 of 43. I'll poll once more and run the comparison as soon as the reversal log completes.
>
> The reversal run has finished. Now I'll read its summary, compare every row with the record's table, and list I2a's 95 failure reasons.
>
> The reversal run completed with all 242 items demonstrated and no changes to the repository. My comparison script flagged three rows that appear to be parser artifacts, so I'll verify those directly, check the mutation run, and then write the report.
>
> I noticed I mistakenly compared the flagged rows against C3's earlier table instead of I2a's own table—I'll redo that comparison correctly and verify the checkout remains unchanged.
>
> All checks are in. Before writing the report I'll load the workspace's reporting skill, since it governs messages that report findings to Nathan, and close out the task list.

The report:

**Verdict: approve.** I2a's harness and record are a sound base for I2b's live runs. There is no blocking finding. Two should-fix findings and four nits remain; one should-fix falls, narrowly, in a class that delays I2b's live runs, and its fix is a few lines that I2b's offline first step can carry before any live call.

- **Prompt received:** revision 1, from commit `9fc3b504ada462ac186aed41852d3978808df95b`.
- **Head reviewed:** `git rev-parse HEAD` printed `6a51dae3e0f2b7a69097151fb5e5dcfe4414b61d`. `HEAD^2` is `761fa289f1dacd13b8d48b78db6b220d07c079e3`. One merge base, `0f45e648099b415217938c25d7369164c0101def`. The ancestor check printed "records build on the head". `git diff --stat HEAD^1 HEAD`: 41 files, 9442 insertions, 246 deletions. The harness under `proofs/` at the head is identical to I2a's code head `7ce93cc`.
- **Environment:** none of `DATABASE_URL`, `HD_API_KEY`, `GEO_API_KEY`, `STREAM_APP_ID`, `STREAM_API_KEY`, `STREAM_API_SECRET` is present. node v24.19.0, npm 11.9.0, npx 11.9.0, Python 3.12.14, all from `/root/.local/bin`.

| Classification (trusted `main` policy, `python3 -I`, outside the tree) | Output |
|---|---|
| `main` → head | `{"full": true, "reason": "behavior-or-empty"}`, 129 paths |
| `8c1a8c0` → head | `{"full": true, "reason": "behavior-or-empty"}`, 53 paths; the filter for non-Markdown files outside `proofs/stream-chat/` printed nothing |
| head → `9fc3b50` | `{"full": false, "reason": "ordinary-docs-only"}`, 5 paths |

##### Findings, most severe first

Paths are under `proofs/stream-chat/`.

**1. Should fix. An interruption inside a family step loses that step's observations.** `glow_stream_proof/mechanisms.py:904` (`collect_after`; the same in `apply`, `:854`).
- **Scenario, reproduced against the fakes:** RV-ban. M1's REST read after the ban succeeds (a "not ended" dimension). A 402 then arrives on M2's read, in the same step. The family's row is the last observed one, "applied: 201", INCONCLUSIVE "interrupted", with no `after` detail and an empty table. M1's observed success is in no row.
- **Why:** a family judges and keeps its row only in `step()`, called after each whole step. Inside a step, only `ClientSessionEnded` is caught per member.
- **Fix:** judge after each member's observations, or wrap each step in `try/finally: self.step(...)`. `step()` sends no request, so it is safe after a signal.
- **Class:** yes, narrowly: it loses the observation a DOES NOT MEET rests on. The row becomes INCONCLUSIVE, never a pass. Run 2 was not interrupted, so no recorded result is affected.

**2. Should fix. The existence oracle can report a false FAIL on two identical successes.** `glow_stream_proof/i2a.py:889`.
- **Scenario, reproduced with `pair_verdict`:** two 200 answers with the same keys whose `duration` strings differ in length (`9.87ms` against `12.34ms`) are "different", because `_normal` compares `len(json.dumps(response))`, and every Stream response carries `duration`. EO-user's `queryUsers` pair would then FAIL as an oracle that is not one.
- **Fix:** drop `duration` before comparing, and compare shape (keys and list lengths), not byte size.
- **Class:** none. A false FAIL, not a false HOLDS. Run 2's EO-user HOLDS is sound: the sizes matched.

**3. Nit (test gaps). Eight fixes still pass every test when broken another way.** I ran 43 mutations of the I2a code in a scratch copy against the full suite without `test_fix_reversals.py`; 35 were caught. The code is correct in each of these; only the test is missing. Class: none.
- `mechanisms.py:1104`: the token margin applied to `rest` only. The one test asserts only `rest`.
- `mechanisms.py:1145`: `listener()` always True. No family test has every session miss the probe, so a broken listener could give a false "ended" unseen by tests.
- `mechanisms.py:1210`: `retained` always True when the channel exists. No test with the channel present and the history message gone.
- `i2a.py:1061`: the oracle HOLDS without a successful control.
- `i2a.py:560`: a write with no answer or a 5xx not counted as `written`, so not restored.
- `i2a.py:896`: 5xx answers treated as determinate (two differing 5xx would FAIL).
- `i2a.py:345`: OUT-send HOLDS with several transport attempts.
- `configuration.py:266`: the type check in `recorded_differences`.

**4. Nit. The guard checks a message's ownership only for a delete.** `glow_stream_proof/guard.py:306`. `POST` and `PUT /messages/{id}`, and `/action`, `/reaction` and `/undelete`, pass on their user IDs alone. Preflight guarantees no other data, and the README's limits say so, so no change can escape in practice. Fix: `owns_message` for every mutating `messages/{id}` path. Class: none, given preflight.

**5. Nit. The client protocol is covered offline for two ops only.** `tests/test_runner.py:93` and `:121` drive the real runner for `set_rest_user` and a channel `call`; `connect`, `guest`, `anonymous`, `disconnect`, `get`, `events` and `channel_data` are covered only by run 2. Fix: one offline test that sends each op the Python side uses and checks the reply's shape. Class: none.

**6. Nit (record).** "A connect with H's old token ... re-creates H" is an inference from the connect's success, not a read of the user; say so. The guard-install reference `proof_run.py:402` is line 395. Class: none.

##### Confirmations and assessments

**The C3 review's items, DM-04's conditions and the independent check:** all confirmed fixed at the head.

| Item | Where confirmed |
|---|---|
| C3 nit 1 (control window searched, B's own read events only left out) | `proof_run.py:2990`, used at `:2908`; reversals 171 to 173 |
| C3 gap (requests between commands, late answers, async errors checked and counted; exit reply; sessions closed before the cleanup is decided) | `client/request-log.cjs`; `client_bridge.py:331`, `:368`, `:432`; `proof_run.py:3349`; reversals 160 to 170 |
| C3 nits 2(a), 2(b), 2(c), 4, 5, 6 | tests added and reversals 174 to 178; the five older stops now go through `ledger.stop_at_once` |
| C3 nit 3 | README, S10 scoped out of the feature-gated sentences |
| DM-04 1, the guard | `guard.py:254`, called from the server client's request hook before the reservation (`server_api.py:127`); the SDK's typed calls use the injected `httpx` client; the SDK's retry policy is disabled by default and retries GET and HEAD only, so nothing is re-sent after a stop |
| DM-04 2, closing checks | `configuration.py:245`; all 19 recorded settings compared, plus two keys absent from the baseline that must stay absent or empty |
| DM-04 3, 4, 5, 6, 7, 8, 9(a) to 9(d) | in-process transport; `only_rate_limit` and `signal_instruction`; `checks/run_plan.py`; undo and "what each member is shown"; the independent check recorded; runs tied to `5df522c` and `7ce93cc`; observation-only server send; `iat` recorded; `include_deactivated_users`; the prompt's wording |
| Independent check 1 to 9 and its nits | each fix present at the lines the record names; each has a reversal (201 to 240) that fails for its stated reason |

**Product findings in "What I2b and P06.2 must know":**
- No mechanism meets the policy on its own: **sound.** Every DOES NOT MEET rests on a 2xx by the member after the mechanism, or on the channel absent from a server read after a delete sent with `conversations: hard`. The two INCONCLUSIVEs are conservative. The revocation's "ends the open subscription" rests on two 2.5 s windows in which M2 received the probe and R did not; a slower delivery is not ruled out, as the record says.
- Free-text paths (invites, AI-indicator events, member custom data, pin and archive flags, a write to the other membership): **sound.** Each FAIL is a 2xx with the text or flag read back by A or B before any control.
- Existence oracles: **sound** for Get Channel and `getMessage` (status and code) and for the channel named in `getReplies` and `getReactions` errors. EO-channel's query and watch pairs rest on message text the row does not keep, as the manager notes; the case's FAIL stands on the GET pair.
- An open WebSocket outlived its token: **sound.** The probe was sent after `exp` plus 3 s and its `message.new` arrived on the expiring session.
- "An old token can re-create the user": the connect's success is sound; the re-creation is inferred (finding 6).

**The manager's decisions:**
- **The disclosure rule: agree.** One detail for I2b: match the carried terms as substrings of the serialized request, because F9-sync carries `{XD}` inside the cid string, and keep the key names of where a term was found.
- **404 code 16 as ended: agree, with one refinement.** Make the second condition checkable in code: the other member's identical request, already collected, still succeeds after the mechanism. That shows the resource exists and only the member's access is gone, and it separates a 404 for a missing membership or user from a 404 for a missing channel. Keep the message as the third condition. Apply it only where the mechanism removes what the request needs, and confirm live with the messages kept, as planned.
- **The poll listing: agree.**
- **The three deviations: agree.** On M1 and M2 shared by the four channel-level mechanisms: each effect is per channel by Stream's documentation, and each family's controls showed M1's reads, writes and subscription intact on the next channel before its mechanism. Putting the wording to the Dev Manager with I2b's prompt is right.

**Areas reviewed with no findings:**
- **The guard:** every mutating server path, the hook order, `cleanup --apply` scoped to the prefix, artifacts recorded before their delete, every type toggle and guest change inside a journalled block, preflight and `verify-clean` read only.
- **Stop paths:** every signal in a reply is recorded before its calls are counted; a signal at exit is recorded always and raised only with nothing in flight (`sys.exc_info` is set inside a `finally`, verified); `finish()` closes the sessions before deciding the cleanup and `cleanup()` checks again; the response hook raises before the SDK sees a 429; the kinds by status, code and wording.
- **Restores and cleanup:** A's member record read before any write and restored and verified after each field; the hide re-hidden before the member's `show`; H named again after a connect; the delete's channel read before the batch; deactivated users listed; the closing checks.
- **The run-1 fix:** only a channel `call` sends `id`, and the runner reads `channel_id`; every command field the runner reads was audited against the Python side.
- **Interrupted rows:** `KEPT_WHEN_INTERRUPTED`, the oracle's per-pair rows, the S15 mapping's per-field rows, pin and archive.
- **The README's rules** match the code for every I2a case; the record's counts add up (114 cases; 85 I1 and 29 I2a; 393 tests; 242 reversals); the two in-place corrections are the C1 finding 5 and nit 13 rows, marked; the eight protected sections are byte-identical at `6e67fd6`, the head and `9fc3b50`.
- **Scope:** only `proofs/stream-chat/**` (40 files) and the evidence record changed; no dependency file, lock, `.npmrc`, `pyproject.toml` dependency or baseline changed; all 41 files mode 100644; no symlink or executable under `proofs/stream-chat/`.

##### Checks and limits

| Check | Result |
|---|---|
| `git diff --check HEAD^1 HEAD` | No output, exit 0 |
| Installs (`env -i`, proxy and CA variables by reference) | `pip check`: "No broken requirements found."; getstream 6.1.0, ruff 0.16.8, mypy 2.3.1. `npm ci --ignore-scripts`: "added 51 packages", "found 0 vulnerabilities" |
| Unit tests (`env -i`) | `Ran 393 tests`, `OK` |
| Ruff check / format / mypy | "All checks passed!" / "51 files already formatted" / "Success: no issues found in 49 source files" |
| `node --check` on the three `.cjs` files | Exit 0, each |
| `checks/run_plan.py` | "run plan: fits", exit 0: complete set 11 users, 18 channels, peak 6 connections, 605 calls on the fakes; reserve 7, 8, 5; no harness errors or problems |
| `checks/fix_reversals.py` | "reversals: 242, not demonstrated: 0", exit 0, 00:30:40 to 00:51:22 UTC (alongside the mutation run). 206 failed on an assertion, 33 on the error their reverted fix causes, 3 aborted on a Ctrl-C by design. All 242 rows match I2a's table by failing test and exception; I read each of I2a's 95 reasons. The checkout was unchanged afterwards |
| Mutations (43, scratch copy, full suite minus the reversal-table test) | 35 caught, 8 survived (finding 3) |
| Probes against the fakes | Finding 1 and finding 2 reproduced |
| Secret scan of `git diff HEAD^1 HEAD` (666,258 bytes) | 0 JWT-shaped strings, emails, private-key blocks, AWS, GitHub or Slack tokens, TLS-weakening settings, environment dumps or secret assignments; the long strings are test names. The client-safe API key, as the four tracked documents record it, appears 0 times |
| Repository | `git status` empty; only ignored paths created; no `.work/`; no commit, push, PR comment, re-run or Notion change |

**Limits:** nothing was run live; the live results rest on I2a's record. I did not read hosted CI and used no sub-agents. The mutation set is mine and not exhaustive. EO-channel's query and watch message texts are not in the record, so their FAIL cannot be checked from it. The two background runs shared the container's CPU, so their timings are not comparable with I2a's.

**NOTHING NEEDED.** Relay this to App Manager 3.

#### Manager verification of the review (App Manager 3, 27 September 2026)

The session committed nothing, so there is no branch to check. The manager checked the report's claims against the reviewed head.

- **Identity and classification.** The prompt revision, the head, its second parent, the merge base and the diff's size are what the prompt expects. The manager's own runs, with the same trusted policy (sha256 `dec69a26…`), gave the report's three results: full scope for 129 paths; full scope for 53 paths, with nothing outside `proofs/stream-chat/`; and `ordinary-docs-only` for 5 paths.
- **Findings, at `6a51dae`,** whose harness is I2a's code head `7ce93cc`:
  - **Finding 1:** a family's row is a snapshot of its state, taken each time it observes (`mechanisms.py:440`). `collect_after` (`:904`) stores each member's reads and writes, and only `step()` (`:1134`), called after the loop over the members (`:921`), judges them into a row. Inside the loop only `ClientSessionEnded` is caught. Any other stop reaches the case loop (`proof_run.py:1243`), and `_interrupted_row` (`:642`) keeps the last row observed, "applied; nothing observed after it yet" (`mechanisms.py:692`), as INCONCLUSIVE. `step()` judges and writes the row, and sends nothing.
  - **Finding 2:** `_normal` (`i2a.py:882`) reduces a success to its keys and `len(json.dumps(response))`, and `pair_verdict` (`:903`) calls any difference a FAIL (`:910`).
  - **Nit 3:** each of the eight lines holds the code the report names. The mutations were the session's own; the manager did not re-run them.
  - **Nit 4:** in the `messages` family, `owns_message` is checked only for a DELETE of `messages/{id}` (`guard.py:306`).
  - **Nit 5, with two corrections:** `RunnerGetTest` (`tests/test_i2a.py:747`) also drives the real runner, with `get`, and checks its budget refusal; and `channel_data` is a parameter of the `call` op, not an op. `connect`, `guest`, `anonymous`, `disconnect` and `events`, a `call` with `channel_data` and a sent `get`'s reply are not covered offline. The nit stands.
  - **Nit 6:** both sentences rest on the connects' success: "which re-creates H", under "Revocation, suspension and deletion", and "can connect afterwards and re-create the user", under "What I2b and P06.2 must know". The line reference stands: `proof_run.py:402` is where the run passes itself to the guard as its scope, which is what the record's sentence says, and `:395` installs the guard.
- **Hosted CI.** On the reviewed head, push run 36278363805 and PR run 36278366585 passed all six jobs (the manager's verification of I2a). The records commits since then are Markdown only:
  - `9fc3b50`: push run [36278735596](https://github.com/amthorn78/glow-dating-app/actions/runs/36278735596) passed, and PR run [36278738109](https://github.com/amthorn78/glow-dating-app/actions/runs/36278738109) passed all six jobs;
  - `2a9f934`: push run [36282606042](https://github.com/amthorn78/glow-dating-app/actions/runs/36282606042) skipped the four application jobs and its gate passed, and PR run [36282609128](https://github.com/amthorn78/glow-dating-app/actions/runs/36282609128) passed all six jobs.
- **Not re-run by the manager:** the session's installs, tests, reversal run, 43 mutations and two probes. Its installs, tests and reversal summary match I2a's record and the manager's own run on `7ce93cc`.

#### Disposition

- **I2a's code head `7ce93cc`, merged at `6a51dae`, is approved.** No finding is blocking, and no recorded result changes.
- **Finding 1 delays I2b's live runs, not the start of I2b.** The review prompt's bound names the live runs, and the reviewer recommends the same: the fix is a few lines, and `step()` sends no request. The brief's shorter wording, "delays I2b", is read the same way, and the Dev Manager reads this reading with I2b's prompt (DM-05). **Required before I2b's first live call:**
  - the fix, in `collect_after` and in `apply`: judge after each member's observations, or keep the row in a `finally` around each step;
  - a test that reproduces the review's scenario (RV-ban; M1's read after the ban succeeds; a 402 on M2's read) and fails without the fix, with its reversal;
  - I2b's independent check before its first live call confirms the fix.
- **I2b's offline first step also takes the rest.** Each code fix gets a test that fails without it and a reversal.
  - **Required:**
    - finding 2: two successes are compared by shape, keys and list lengths, without `duration`. Each pair keeps both normalized messages, as already planned;
    - nit 3's listener and retention tests (`mechanisms.py:1145` and `:1210`), because I2b changes `mechanisms.py` and a broken listener could give a false "ended";
    - nit 4: `owns_message` for every mutating `messages/{id}` path;
    - nit 5: one offline test that sends the real runner each op the Python side uses, and checks the reply's shape;
    - nit 6: the two sentences corrected in place and marked "(corrected in P06.1-I2b)". The re-creation is inferred from the connects' success; no read of the user shows it.
  - **Fixed, or left with a one-line reason:** nit 3's other six tests.
- **The manager's decisions, as the review leaves them,** for I2b's runs:
  - **The disclosure rule** (F9-thread and F9-sync): the scan leaves out every term that appears, as a substring, anywhere in the serialized request (path, query and body), because the sender already had it. F9-sync carries `{XD}` inside the cid. The row keeps the key names of the response where a term was found.
  - **404 code 16 as "ended":** only when all three hold:
    - the same request by the same member succeeded before the mechanism;
    - the other member's identical request, already collected, still succeeds after it;
    - Stream's message, kept in the row, names the missing membership or user.

    It applies only where the mechanism removes what the request needs: the membership after a removal, the user after a deactivation. Otherwise the dimension stays "not shown". I2b reruns RV-remove and SD-deactivate live under it, and I2b's review confirms the result before any design rests on it (DM-01 P4).
  - **The poll listing and the three deviations:** as decided. The Dev Manager reads the wording on M1 and M2, shared by the four channel-level mechanisms, with I2b's prompt.
- **I2b's prompt is next.** It authorizes credential use and live provider actions, so the Dev Manager reads it before Nathan runs it (DM-05).
- *App Manager 4, 27 September 2026:* DM-05 read revision 1 and approved it with conditions. It agreed with this reading of finding 1 (its finding 8) and with the manager's reading of the shared M1 and M2 (its finding 7), and set six conditions, which revision 2 of the prompt applies. See the review log, "DM-05".

## P06.1-I2b

Nathan ran this session from revision 2 of the [I2b implementation prompt](../../ephemeral/2026-09-27-p06-1-i2b-implementation-prompt.md), from commit `b04306d67c79d3a2ff1981d6bc3c65ca0de24bd1` (App Manager 4's manager branch `claude/stoic-carson-66gdig`), on the session branch `claude/confident-brown-baykju`. Head: the harness at `ad89753` (the last code commit; the runs ran from `2ff6807`, `93390ce` and `ad89753`); this section and the architecture document are the commit after it, the branch head named in the session's report. The prompt and DM-05's report differed in no point of substance that changed the work. At session start the manager branch's head was one Markdown-only commit ahead of `b04306d`; the prompt was read at `b04306d` as directed.

### Environment

- None of `DATABASE_URL`, `HD_API_KEY` or `GEO_API_KEY` was present. `STREAM_APP_ID`, `STREAM_API_KEY` and `STREAM_API_SECRET` were set (names checked only). node v24.19.0, npm 11.9.0, npx 11.9.0 and Python 3.12.14, from `/root/.local/bin`.
- The start gate passed: `HEAD` was `b04306d`; `git diff --stat 6a51dae HEAD -- proofs/stream-chat/` and `git diff --stat origin/main HEAD -- .github/` printed nothing. The `.github` diff was checked against `origin/main` at `0f45e64`.
- Offline commands ran under `env -i` without any `STREAM_*` variable; the installs got the proxy and CA variables by reference; every live command ran through a launcher (the session's own, outside the repository) that inherits only the path, home, locale, proxy and CA variables and the three `STREAM_*` variables, refuses to start if an HDE variable is present, refuses `restore`, the general `configure --apply`, `cleanup` without `--apply` and any command the plan does not name, writes the output to a log and prints only a scan of it (the secret, JWT-shaped strings and the API key, each counted) before the log is read. No output held the secret, a token or the API key.

### Step 1: the I2a review's items, the two rules and the Foundation job (`bca64eb`)

Each item, with its test and reversal (`checks/fix_reversals.py`, the "I2b …" entries):

- **Finding 1** (`mechanisms.py`, `Family.execute`, `stepping`, `apply`, `after_apply`, `collect_after`): a family judges and keeps its row after every part of a step, in a `finally` (`stepping`), so a stop on one member's request inside a step no longer loses another member's observation; once the mechanism's request is answered the row says `applied: …`. Tests: `tests/test_mechanisms.py` `KeptStepsTest` (the review's scenario: RV-ban, M1's read succeeds, a 402 on M2's read; the row keeps M1's read as DOES NOT MEET), three reversals.
- **Finding 2** (`i2a.py`, `shape`, `_normal`, `normalized`, `pair_verdict`): two successes compare by shape (key names at every level, list lengths, scalar types) with `duration` left out, never by size; each pair keeps `existing_normalized` and `missing_normalized`. Tests: `tests/test_i2a.py` `OracleTest`; three reversals.
- **Nit 3**: the listener test (every session misses the probe: `not shown`), the retention test (the channel present and its first message gone: DOES NOT MEET), the token margin on every dimension, the oracle's control, a 5xx pair, a write answered 5xx or not at all put back, several transport attempts in OUT-send, and the type of a recorded setting: eight tests, eight reversals (`tests/test_mechanisms.py`, `tests/test_i2a.py`, `tests/test_configuration.py`). None of the eight was left.
- **Nit 4** (`guard.py`, the `messages` family): every mutating `messages/{id}` path needs a message the run recorded; the run records S10's poll message so the server's vote passes. Tests: `tests/test_guard.py` `RefusalTest.test_a_message_poll_or_group_must_be_the_runs` and `ServerHookTest.test_the_message_rule_in_the_real_hook` (the real `ServerApi` hook on an `httpx.MockTransport`, raw and typed, with the controls' shapes on a recorded message). Live: S3a in run 1 (below).
- **Nit 5** (`tests/test_runner.py` `EveryOpTest`): the real runner, offline, answers every op the Python side uses (`ping`, `selfcheck`, `connect`, `disconnect`, `set_rest_user`, a channel `call` with `channel_data`, a client `call`, `get`, `guest`, `anonymous`, `events`, and since step 2 `product`) with a reply of the protocol's shape, nothing sent.
- **Nit 6**: the two sentences on H's re-creation corrected in place above, marked "(corrected in P06.1-I2b; the I2a review's nit 6)".
- **The disclosure rule** (`proof_run.py` `_disclosure`; `matrix.carried_terms`, `term_paths`): a term present as a substring anywhere in the serialized request is left out; the row's `disclosure` detail keeps `terms_in_the_request` and `found_at`. Tests: `tests/test_answers.py` `DisclosureRuleTest`; three reversals.
- **404 code 16** (`mechanisms.py` `missing_404`, `dimension`, `token_dimension`, `judge_dimensions`, `refusal_messages`, `other_ok`): ended only when the member's same request succeeded before, the other member's identical request still succeeds after, and Stream's message, kept in `after.<member>.messages`, names the missing membership or user; only after RV-remove and SD-deactivate. Tests: `tests/test_mechanisms.py` `Missing404Test`; five reversals.
- **The `sync` pair** in EO-channel; **the API key** removed from free text (`redaction.Redactor(api_key=…)`, given by `cli.Context`); **the poll listing**: polls listed as each of the run's own users before their delete (`POST /api/v2/polls/query?user_id=…`, a deactivated user left out) and each recorded poll read by ID after its delete (must be 404); the standalone listing stays "not verified" and says why. Tests and reversals for each.
- **The Foundation job** `proof` ("Stream proof checks"): the hash-locked install and `pip check`, `npm ci --ignore-scripts`, the tests under `env -i`, Ruff, mypy, `node --check` on every `.cjs` file and `checks/run_plan.py`; the same `if:` as the other application jobs, the same action pins, `persist-credentials: false`, `working-directory: proofs/stream-chat`, `python-version: '3.12.14'`, `node-version: '24.19.0'`, one `npm install --global npm@11.9.0` right after setup-node with `working-directory: ${{ github.workspace }}`, `timeout-minutes: 10`, no `secrets.*`, no `env:`; added to the gate's `needs` and its Python tuple. The pin test (`services/api`, `python3.12 -m unittest tests.test_toolchain_pins`): 3 tests, OK at both commits that touch the workflow (only `bca64eb` does). **First result**: Foundation run 305 on `bca64eb` (https://github.com/amthorn78/glow-dating-app/actions/runs/36291354418), 03:25:22 to 03:30:46 UTC, conclusion success, 7 jobs; "Stream proof checks" ran (not skipped), 03:25:33 to 03:26:41, every step success (the tests in 37 s), and the gate passed. `npm audit` (DM-02 B9, optional): `npm audit` in `proofs/stream-chat` (the lockfile's tree, no install) printed "found 0 vulnerabilities".

Step 1's checks at `bca64eb`: 426 tests OK; Ruff "All checks passed!" and "51 files already formatted"; mypy "Success: no issues found in 49 source files"; `node --check` OK for the three `.cjs` files; `checks/run_plan.py` "run plan: fits"; `checks/fix_reversals.py` "reversals: 274, not demonstrated: 0" (03:04:08 to 03:22:04 UTC); every I2b reversal's failure reason read: each fails on the assertion or error its rule names (for example finding 1's "'INCONCLUSIVE' != 'DOES NOT MEET the history policy'", nit 4's "GuardRefused not raised", the disclosure rule's "'FAIL' != 'HOLDS (filtered, not refused)'", the 404 rule's "'ended' != 'not shown'").

### Step 2: Video and Feeds, offline (`a1880fb`)

**Stream behaviour, from Stream's documentation and `getstream` 6.1.0** (a read-only research sub-agent on getstream.io and the installed SDK sources; no Stream call):

- **Where grants live.** "Chat grants permissions per channel type or per channel, Feeds per feed visibility, and Video per call type"; the `.app` scope "exists in every product and applies to operations that occur outside product resources" (Stream, Platform, "Permissions"); I1 already emptied it for `user`, `guest` and `anonymous`. Feed groups carry no grants (`FeedGroupResponse`: `default_visibility`, `default_follower_role`). "A grants update only changes the roles mentioned in the request. Providing an empty array as a role's permission list removes all grants for that role" (same page): the plan names only the client roles with `[]`.
- **Paths** (`getstream` 6.1.0 `video/rest_client.py`, `feeds/rest_client.py`): `GET /api/v2/video/calltypes` (`ListCallTypeResponse.call_types: dict[name, CallTypeResponse{grants, settings, notification_settings}]`), `PUT /api/v2/video/calltypes/{name}` (`grants`, `settings`, `notification_settings`, `external_storage`); `GET /api/v2/feeds/feed_visibilities` (`feed_visibilities: dict[name, {grants}]`), `PUT /api/v2/feeds/feed_visibilities/{name}` (`grants`); `GET /api/v2/feeds/feed_groups` (`groups`). The requests the cases send and the deletes cleanup uses are listed in the README ("P06.1-I2b cases", "The guard"). The server SDK sends every product's requests to one base URL, `https://chat.stream-io-api.com/` (`stream.py`), which the runner's op uses too.
- **Availability.** Stream documents no "product not enabled" error; its Feeds migration guide says a 404 means "the endpoints are not yet available on your app's deployment"; the nearest error-table entries are 17 (Not Allowed), 19 (feature disabled on the dashboard), 99 (app suspended) and 16 (does not exist). The probe is one configuration read per product (`GET /api/v2/video/calltypes`; `GET /api/v2/feeds/feed_visibilities` and `GET /api/v2/feeds/feed_groups`).
- **What a user token can do by default.** Not published: the built-in call types' and the visibilities' default grants are in the dashboard only; the built-in `development` type has "all permissions enabled for testing purposes". Video's permission names include `create-call`, `read-call`, `update-call`, `update-call-settings`, `update-call-member`, `join-call`; there is no `send-event` capability, so the grant governing a custom call event is not documented. Feeds' capability names include `create-feed`, `read-feed`, `read-activities`, `add-activity`, `add-comment`, `add-activity-reaction`, `follow`, `update-feed`; which grant each request needs is not documented. The live runs show what the application grants.
- **Reach to the other member.** A call's `custom` data is read back by any member (`GET`) and `call.updated` reaches watchers; a custom call event (`POST …/event`) dispatches the `custom` WebSocket event to the call's members; `call.member_added` reaches every member without `ring` or `notify`; a feed's activities, comments and reactions are readable by whoever may read the feed (the "visible" and "public" visibilities let anyone view). The runner holds a chat WebSocket only, so Video's events are not observed; the reads are.
- **Cost.** Video is billed in participant minutes ("If 7 users talk for 10 minutes, the total number of participant minutes is 7 * 10 = 70"; getstream.io/video/pricing); no request the cases send joins a call or starts media, so none is a participant minute. Feeds' Build plan: 125,000 API calls and 5,000 activities a month, overage "Not allowed" (getstream.io/activity-feeds/pricing); the Maker account: "With hard limits in place, you'll never face surprise overages" (getstream.io/blog/maker-account). The runs send a few dozen Feeds requests and create under ten activities. No request whose cost was unclear was made; whether a Video API call without a join is billed is not documented, and Stream's pricing names no such unit.
- **Deletability.** `delete_call(type, id, hard=True)` = `POST /api/v2/video/call/{type}/{id}/delete` `{"hard": true}` ("completely wiped out … irrevocable", async `task_id`); `delete_feed` = `DELETE /api/v2/feeds/feed_groups/{g}/feeds/{id}?hard_delete=true` (cascades to follows, members, activities, reactions, bookmarks, comments); `delete_activity`, `delete_comment` (`?hard_delete=true`), `delete_activity_reaction` (`?user_id=`), `unfollow` (`DELETE /api/v2/feeds/follows/{source}/{target}`); and a user's Feeds data, `POST /api/v2/feeds/users/{user_id}/delete` (feeds, activities, comments, reactions, follows). A hard user delete's `calls: "hard"` removes only 1:1 calls. Every object a case creates has one of these deletes; cleanup sends them all.

**The harness.** The README's "P06.1-I2b cases", "The guard" and "The Video and Feeds lockdown" state the rules; in short:

- the runner's `product` op (`client/product-op.cjs`) and the guard's Video and Feeds scope (`glow_stream_proof/products.py`, `guard.py`): the same allowlist in both (a test drives the JS file with node and compares every row of a table with the Python table), the deny-list first (`join`, `go_live`, `start_`, `stop_`, `broadcast`, `recording`, `transcription`, `caption`, `ring`, `notify`, `rtmp`, `hls`, `egress`; `ring`, `notify`, `video: true`, `create_notification_activity: true`), a configuration write only in `guard.ConfigureScope`, deletes only of run-owned objects;
- 18 cases (`matrix._products`), fixtures once per run, objects recorded from every answer, one undo per object (`Control.undo_once`), the product-finding rule and the `NOT AVAILABLE` verdict, the `upgrade`-only exemption in `usage.charge_signal`;
- `configure --products video,feeds` (a difference; `--apply` refuses in code while chat does not verify, for any path outside the two configuration families and for an unknown product; runs in the configure scope; re-reads and verifies), `configuration.verify` comparing the products from `products.LOCKDOWN_APPLIED` on, `probe-products`, `record-products-baseline`, the listings in `baseline`, preflight, `verify-clean` and `cleanup`;
- the lean setup for a run of product cases alone; `checks/run_plan.py` counting run 1, run V1, run V2 and the largest in reserve; the end-of-run reserve raised from 130 to 190 calls (the measured worst case with one object of every kind is 172);
- `tests/fake_products.py`: a model of both products with knobs for availability, the user role's capabilities and the resource roles' (its defaults are guesses).

Step 2's checks at `a1880fb`: 496 tests OK; Ruff "All checks passed!" and "55 files already formatted"; mypy "Success: no issues found in 53 source files"; `node --check` OK for the four `.cjs` files; `checks/run_plan.py` "run plan: fits"; the pin test OK; `checks/fix_reversals.py` the 56 new entries demonstrated as a subset before the commit (04:11 UTC; two patterns then repaired for Ruff's formatting) and the whole set demonstrated at `2ff6807` (below), which holds the same entries. Foundation run 306 on `a1880fb`: https://github.com/amthorn78/glow-dating-app/actions/runs/36293690703, 04:13:38 to 04:19:50 UTC, success, 7 jobs; "Stream proof checks" 04:13:49 to 04:15:01, every step success (tests 38 s, `run_plan.py` success); the gate passed.

### The independent check before the first live call

A fresh reader (a read-only sub-agent of this session, given the seven areas of the prompt's section 5 as its brief: no network, no `STREAM_*` variable, no change, no `fix_reversals.py`) checked steps 1 and 2 at `a1880fb`. It found no way to a false pass. Its findings, fixed at `2ff6807` (https://github.com/amthorn78/glow-dating-app/actions/runs/36295196205: Foundation run 307, 04:44:46 to 04:50:59 UTC, success; "Stream proof checks" 04:44:58 to 04:46:16, every step success), each with a failing test and a reversal (the "I2b check N" entries):

1. **Could lose a DOES NOT MEET** (`mechanisms.py`, `undo`): the member's own undo (RV-hide's show, the rejoin, the unban, the unfreeze) is now judged from the client's answer before the control's replay, so a stop in the replay keeps the client's success as FAIL in the row (`undo_verdict`, `client_undo.control: "not completed"`).
2. **Could lose an observation** (`mechanisms.py`, `events`, `probes`): each session's event window is kept as it is collected, so a stop on a later session's collection keeps an earlier member's "probe received" as its subscription dimension.
3. **Could judge an input error as a product finding, and could stop for nothing** (`usage.py`, `products.py`, `proof_run.py`): the product wording needs the product, feature, application or plan as its subject and no object or field of the request ("feed group 'x' is not available" is an input error); a 404 to a case's request is an object that does not exist; a listing of calls, feeds or activities that is not 2xx is "not available" only by the product's own configuration read, never by the listing's message; preflight stops on a listing that is not verified, as it does for the channels.
4. **Nit** (`guard.py`): the configure scope passes a `PUT` only with the lockdown's body (grants alone, client roles only, each `[]`).
5. **Nit** (`cli.py`): the scoped apply is gated by the chat verification alone, so it can re-apply once the lockdown is recorded.
6. **Nit** (`products.py`, `product-op.cjs`): the Python and JS tables agree on the denied value (a boolean true or `"true"`) and on the order of their reasons.

Three remarks were recorded as limits in the README ("Limits", "Added in P06.1-I2b") rather than changed: the oracle's shape compares scalar types, not values, and the word "user" in a product answer counts as an object word; the standalone `cleanup --apply` removes activities only through the proof users' Feeds data delete; the member's own `updateMemberPartial` and the Feeds updates carry no `skip_push` (the requests have no such field). Checks at `2ff6807`: 501 tests OK; Ruff, mypy, `node --check`, the run plan and the pin test pass; `checks/fix_reversals.py` "reversals: 341, not demonstrated: 0" (04:45:07 to 05:12:53 UTC).

### The run plan's count

`checks/run_plan.py` at `2ff6807` (unchanged by the later commits), offline against the fakes, with this checkout's ledger at zero:

| Set | Users | Channels | Peak connections | API calls (fakes) | Cases |
|---|---|---|---|---|---|
| Run 1 (RV-remove, SD-deactivate, F9-thread, F9-sync, EO-channel, EO-user, EO-message, S3a) | 7 | 4 | 4 | 129 | 8 |
| Run V1 (the 18 Video and Feeds cases, lean setup) | 2 | 0 | 2 | 96 | 18 |
| Run V2 (the same, after the lockdown) | 2 | 0 | 2 | 96 | 18 |
| Largest run, in reserve | 7 | 4 | 4 | 129 | |
| **Total** | **18 of 20** | **8 of 30** (+1 if EO-channel's probe creates the missing channel) | 4 of 10 | 450 of 5,000 | |

The complete set (132 cases) still counts 11 users, 18 channels and a peak of 6 connections, with the largest family (7, 8, 5) in reserve. `all_fit: true`.

### Live commands (27 September 2026, UTC; one checkout, one command at a time)

Every command ran from a committed and pushed head at which the offline checks and the fix reversals had passed; the environment held no HDE variable; every log's scan counted 0 for the secret, 0 JWT-shaped strings and 0 for the API key, and so did every results file read afterwards.

| # | Command (head) | Start to end (UTC) | Exit | Result |
|---|---|---|---|---|
| 1 | `verify-clean` (`2ff6807`) | 04:45:07 to 04:45:10 | 1 | Clean apart from the standalone poll listing, which is "not verified" by design: proof users `[]`, channels `[]`, other users 1 (the dashboard user), user groups `[]`, calls `[]`, feeds `[]`, activities `[]` |
| 2 | `configure` (dry run; `2ff6807`) | 04:45:10 to 04:45:12 | 0 | "differences before: []"; the seven-step chat plan printed, nothing sent |
| 3 | `configure --products video,feeds` (dry run; `2ff6807`) | 04:45:44 to 04:45:46 | 0 | Both products available; 18 differences; a plan of 9 `PUT`s (`audio_room`: user, anonymous; `default`: user, guest; `development`: user, guest, anonymous; `livestream`: user, anonymous; `followers`, `members`, `private`: user; `public`, `visible`: user, guest, anonymous); nothing sent |
| 4 | `run --accept-dashboard-user --only RV-remove,SD-deactivate,F9-thread,F9-sync,EO-channel,EO-user,EO-message,S3a` (run 1, `p061i1-0927051318`; `2ff6807`) | 05:13:16 to 05:14:20 | 0 | 20 authorized-path checks PASS; RV-remove MEETS, SD-deactivate MEETS, EO-channel FAIL, EO-user HOLDS, EO-message FAIL, F9-thread INCONCLUSIVE, F9-sync HOLDS (filtered), S3a HOLDS. Usage: 7 users, 4 channels, 145 calls (94 server, 51 client), peak 4 connections. Cleanup complete (below); no stop, no signal |
| 5 | `probe-products` (`2ff6807`) | 05:17:42 to 05:17:44 | 0 | Video available (`GET /api/v2/video/calltypes` 200); Feeds available (`GET /api/v2/feeds/feed_visibilities`, `GET /api/v2/feeds/feed_groups` 200); call types `audio_room`, `default`, `development`, `livestream`; visibilities `followers`, `members`, `private`, `public`, `visible`; groups `foryou`, `notification`, `stories`, `story`, `timeline`, `user` |
| 6 | `run --accept-dashboard-user --only <the 18 VD and FD cases>` (run V1, `p061i1-0927051807`; `2ff6807`) | 05:18:05 to 05:18:30 | 0 | Lean setup, 3 checks PASS; Video 8 FAIL; Feeds: FD-feed HOLDS, FD-other-feed HOLDS, 8 INCONCLUSIVE (the fixture of A's feed 404 code 16 "feed with id … has been deleted" after FD-feed's undo: a harness defect, fixed at `93390ce`). Usage: 2 users, 0 channels, 98 calls (87 server, 11 client), peak 2. Cleanup complete; no stop, no signal |
| 7 | `baseline` (`2ff6807`) | 05:22:39 to 05:22:42 | 0 | `.work/snapshot-20260927T052241Z.json`; chat differences 0; both products available; 18 Video and Feeds differences from the lockdown target (the same 18 as the dry run) |
| 8 | `record-products-baseline --snapshot .work/snapshot-20260927T052241Z.json` (`2ff6807`; no network) | 05:23:03 to 05:23:05 | 0 | `baseline/video-feeds-1729640-2026-09-27.json` (130,016 bytes; scanned; committed at `1137786`) |
| 9 | `run --accept-dashboard-user --only <the 18 VD and FD cases>` (run V1 rerun, the reserve rerun, `p061i1-0927055652`; `93390ce`) | 05:56:51 to 05:57:22 | 0 | Lean setup, 3 checks PASS; 16 FAIL, 2 HOLDS (FD-feed, FD-other-feed); no INCONCLUSIVE. Usage: 2 users, 0 channels, 124 calls (104 server, 20 client), peak 2. Cleanup complete; no stop, no signal |
| 10 | `configure --products video,feeds` (dry run; `93390ce`) | 05:57:54 to 05:57:57 | 0 | Identical to command 3: chat differences `[]`, 18 differences, the same 9 `PUT`s; nothing sent |
| 11 | `configure --products video,feeds --apply` (the one lasting change; `93390ce`) | 05:58:27 to 05:58:31 | 0 | Chat differences `[]`; the 9 `PUT`s each answered 201; the re-read shows every client role at `[]` in the four call types and the five visibilities; "differences after: []"; local record `.work/configure-products-20260927T055831Z.json` (scanned) |
| 12 | `run --accept-dashboard-user --only <the 18 VD and FD cases>` (run V2, `p061i1-0927062935`; `ad89753`) | 06:29:34 to 06:30:05 | 0 | Preflight `configuration_problems: []` (the lockdown verified); lean setup, 3 checks PASS; 9 HOLDS, 7 FAIL, 2 INCONCLUSIVE. Usage: 2 users, 0 channels, 123 calls (103 server, 20 client), peak 2. Cleanup complete; no stop, no signal |
| 13 | `verify-clean` (`ad89753`) | 06:30:48 to 06:30:50 | 1 | Clean apart from the standalone poll listing ("not verified", by design): proof users `[]`, channels `[]`, other users 1, user groups `[]`, calls `[]`, feeds `[]`, activities `[]` |
| 14 | `configure` (dry run; `ad89753`) | 06:30:50 to 06:30:52 | 0 | "differences before: []" (the chat configuration verifies, products included); the seven-step plan printed, nothing sent |
| 15 | `configure --products video,feeds` (dry run; `ad89753`) | 06:30:52 to 06:30:55 | 0 | "differences before: []", "video and feeds differences before: []", "video and feeds plan: nothing to change" |

No `cleanup --apply` was needed: every run's own cleanup completed and the listings after the last run are empty. Session usage after the last run: 13 users, 4 channels, 560 API calls (458 server, 102 client), peak 4 connections, 18 connection attempts, of 20, 30, 5,000 and 10.

### Results by topic

**Run 1 (`p061i1-0927051318`, the chat reruns under the new rules; full setup, 20 authorized-path checks PASS).**

| Case | Verdict | What was observed |
|---|---|---|
| RV-remove | MEETS the history policy | M1 after its removal: REST read 403 code 17; the open subscription ended (no probe received); a reused token refused; its own member write (`updateMemberPartial`, S15) 404 code 16 `UpdateMemberPartial failed with error: "user is not a member of the channel"`, with M2's identical write succeeding after it (the 404 code 16 rule's three conditions met and the message kept in the row); the history retained; M1's own undo (a rejoin) HOLDS |
| SD-deactivate | MEETS | S: REST read and member write 404 code 16 `the user … was deactivated`; the open subscription ended; a reused token and a token issued after the deactivation both refused at connect (`WS failed with code 16 and reason - the user … was deactivated`); M2 unaffected on every dimension; the history retained |
| EO-channel | FAIL | Get Channel: 403 code 17 for the existing channel against 404 code 16 `Can't find channel with id glow-match:…` for the missing one; `query` and `watch`: 403 code 17 for both but messages naming different actions (ReadChannel against CreateChannel); `sync`: 201 for both, but the answers differ in shape (a list of two entries against one). The row keeps both normalized answers of every pair, but in I2b's local results file, which was not kept: no record holds the `sync` pair's two normalized answers, and they are not reconstructed here (corrected in P06.1-C4; the I2b review's nit 10) |
| EO-user | HOLDS | Both answers of the same shape |
| EO-message | FAIL | 403 code 17 for the existing message against 404 code 16 `message with id … doesn't exist` |
| F9-thread | INCONCLUSIVE | 404 code 16 `Thread with id … doesn't exist` for the member and the non-member alike: with `replies` off in `glow-match` no thread exists, so the control did not succeed. The disclosure detail records the message ID the request carried (`terms_in_the_request`) and nothing found |
| F9-sync | HOLDS (filtered, not refused) | The only term found was the channel ID the request itself carried (`terms_in_the_request: [{XD}]`); nothing of the other channel's content |
| S3a | HOLDS | The client's write to another message 403 code 17; the server's replay 201; its undo 201 (nit 4's guard rule exercised live: the run recorded the message) |

Cleanup: polls listed as each of the six run users before their delete (the deactivated user left out, `listing: verified`, `remaining_polls: []`); channels and users deleted (task completed); the one deleted-user artifact found and deleted; `product_deletes: []`; every remaining list empty; no stop, no signal, no note. Usage: 7 users, 4 channels, 145 API calls (94 server, 51 client), peak 4 connections, 12 connection attempts.

**Run V1 (`p061i1-0927055652`, the reserve rerun; the first attempt `p061i1-0927051807` is below under deviations).** Lean setup (A and B, no channel); AP1, AP4-A, AP4-B PASS. Every case's request is the client's own, with A's or B's token, through the runner's `product` op.

| Case | Verdict | Client's request and answer | Control |
|---|---|---|---|
| VD-create | FAIL | `POST /api/v2/video/call/default/{CALL_a}` with custom data and A and B as members: 201 | server replay 201, undo 201 (the client's call undone once, by the replay's undo) |
| VD-create-dev | FAIL | `POST /api/v2/video/call/development/{CALL_dev}`: 201 | replay 201, undo 201 |
| VD-read | FAIL | `GET /api/v2/video/call/default/{CALL}` (a call the server created with A and B): 200 | replay 200 |
| VD-read-other | FAIL (disclosed) | B `GET /api/v2/video/call/default/{CALL_x}` (A's call, B not a member): 200; found A's ID at `call.created_by.id`, `members[].user_id` and the free text at `call.custom.glow_note` | A's own read 200 with the same data |
| VD-update | FAIL | `PATCH …/{CALL}` custom data: 200 | replay 200, undo 200 |
| VD-members | FAIL | `POST …/{CALL_x}/members` adding B: 201 | replay 201, undo 201 |
| VD-event | FAIL | `POST …/{CALL}/event` with free text: 201 | replay 201 |
| VD-query | FAIL (disclosed) | B `POST /api/v2/video/calls` filtered on A: 201; found A's call ID and the free text | replay 201 |
| FD-feed | HOLDS | `POST /api/v2/feeds/feed_groups/user/feeds/{A}`: 403 code 17 `User '…' with role 'user' is not allowed to perform action CreateFeed` | replay 201 (the feed stays for the later cases) |
| FD-activity | FAIL | `POST /api/v2/feeds/activities` into A's feed with free text: 201 | replay 201 |
| FD-other-feed | HOLDS | `POST /api/v2/feeds/activities` into B's feed: 403 code 17 `User does not have permission to add activities to feeds: user:…` | replay 201 |
| FD-read | FAIL (disclosed) | B `POST …/feed_groups/user/feeds/{A}` (read): 201; found the free text and the activity ID | A's own read 201 |
| FD-query | FAIL (disclosed) | B `POST /api/v2/feeds/activities/query` filtered on A: 201; found the free text and the activity ID | replay 201 |
| FD-follow | FAIL | B `POST /api/v2/feeds/follows` (B's timeline follows A's feed): 201 | replay 400 code 4 `Follow … already exists in accepted state` (the client's follow was in place); the client's follow undone |
| FD-comment | FAIL | B `POST /api/v2/feeds/comments` on A's activity: 201 | replay 201 |
| FD-reaction | FAIL | B `POST /api/v2/feeds/activities/{ACT}/reactions`: 201 | replay 201, undo 200 |
| FD-update | FAIL | A `PUT /api/v2/feeds/activities/{ACT}` (text and custom data): 201 | replay 400 code 4 `No changes detected …` (the client's update was in place) |
| FD-feed-custom | FAIL | A `PUT …/feed_groups/user/feeds/{A}` custom data: 201 | replay 201, undo 201 |

So with the application's default grants a user token had, in Video, every capability the cases test (the `user` role's grants in section 5 of the architecture document include `create-call`, `read-call`, `update-call-member`, `send-event`; the read of another user's call and the query are not member-bound), and in Feeds everything except creating a feed and posting into another user's feed (the `user` and `timeline` groups' default visibility is `visible`, whose `user` grants include `read-feed`, `read-activities`, `add-comment`, `add-activity-reaction`, `follow` and `add-activities-owner`). Cleanup: 17 product deletes (a reaction and a follow already undone, 404; comments, activities and feeds 200; two calls already undone, 404, two deleted; both users' Feeds data deleted); users and the artifact deleted; every remaining list empty; no stop, no signal. Usage: 2 users, 0 channels, 124 API calls (104 server, 20 client), peak 2.

**The lockdown (command 11).** The plan of section 5 of the architecture document, applied once; nine `PUT`s, each 201; the re-read verified both products; `differences after: []`. From `ad89753` on, `configuration.verify` compares the products, so run V2's preflight verified the lockdown before running.

**Run V2 (`p061i1-0927062935`, after the lockdown).** Lean setup; preflight verified the lockdown (`configuration_problems: []`).

| Case | Verdict | Client's request and answer | Control |
|---|---|---|---|
| VD-create | HOLDS | 403 code 17 | replay 201, undo 201 |
| VD-create-dev | HOLDS | 403 code 17 | replay 201, undo 201 |
| VD-read | FAIL | 200 (A is a member of the call the server created) | replay 200 |
| VD-read-other | HOLDS | 403 code 17 `GetCall failed with error: "User '…' with role 'user' is not allowed to perform action ReadCall in scope 'video:default'"`; nothing found | A's own read 200 |
| VD-update | FAIL | 200 (a member's update of the call's custom data) | replay 200, undo 200 |
| VD-members | FAIL | 201 (A adds B to A's own call) | replay 201, undo 201 |
| VD-event | FAIL | 201 (a member's custom event with free text) | replay 201 |
| VD-query | INCONCLUSIVE (refusal not attributable, code 102) | 403 code 102 `QueryCalls failed with error: "some calls match your query but cannot be returned because you don't have access to them. Did you forget to include {members: $in: [...]}?"`; nothing found | replay 201 with A's call |
| FD-feed | HOLDS | 403 code 17 | replay 201 |
| FD-activity | FAIL | 201 (the feed's creator adds an activity) | replay 201 |
| FD-other-feed | HOLDS | 403 code 17 | replay 201 |
| FD-read | INCONCLUSIVE (permission error, but the positive control did not succeed) | B: 403 code 17 `GetOrCreateFeed failed with error: "… not allowed to perform action ReadFeed in scope 'feeds:visible'"` | A's own read: 403 code 17 too |
| FD-query | FAIL (disclosed) | B `POST /api/v2/feeds/activities/query` filtered on A: 201; found the free text at `activities[].text` and the activity ID at `activities[].id` | replay 201 |
| FD-follow | HOLDS | 403 code 17 | replay 201, undo 200 |
| FD-comment | HOLDS | 403 code 17 | replay 201 |
| FD-reaction | HOLDS | 403 code 17 | replay 201, undo 200 |
| FD-update | FAIL | 201 (the activity's owner edits it) | replay 400 code 4 `No changes detected …`; the client's edit undone (PUT 201) |
| FD-feed-custom | HOLDS | 403 code 17 `UpdateFeed failed with error: "… not allowed to perform action UpdateFeed in scope 'feeds:visible'"` | replay 201, undo 201 |

Read against V1: the lockdown removed every capability the `user` role granted (creating calls, reading and querying other users' calls, reading other users' feeds, following, commenting, reacting, updating a feed's custom data, and the owner's own feed read). What remains is held by roles the plan does not touch (a call's `call_member` and creator; a feed's creator; see section 6 of the architecture document) and one read the plan does not govern: the activities query still returns another user's activities with their text and IDs, with the `.app` scope and every client grant empty. Stream does not document which grant governs `QueryActivities`; the proof found no configuration that refuses it, and records it for Nathan's decision. The refused calls query's message tells the caller that matching calls exist. Cleanup: 16 product deletes (a reaction and a follow undone by the replays, 404; a comment, four activities and three feeds 200; two calls undone, 404, two deleted 201; both users' Feeds data deleted); users and the artifact deleted; every remaining list empty; no stop, no signal. Usage: 2 users, 0 channels, 123 API calls (103 server, 20 client), peak 2.

### Records

- `docs/architecture/chat-provider-permissions.md`, new (DM-02 B7; DM-05 finding 5).
- `proofs/stream-chat/README.md`: layout, live commands, the run's steps, "P06.1-I2b cases", the run plan, "Signals, by kind", the guard's Video and Feeds scope and the runner's op, "The Video and Feeds lockdown", "What this proof does not show", "Limits".
- This record: this section, and the two nit 6 corrections in "P06.1-I2a", marked.

### Checks

Section 7's checks, at the head named above (`ad89753` for the code; the records commit adds two Markdown files and one README line and changes no code):

1. `git diff --check b04306d HEAD`: no whitespace problem. `git diff --name-only b04306d HEAD`: 41 paths, every one in the owned paths (`.github/workflows/foundation.yml`; `docs/architecture/chat-provider-permissions.md`; this record; `proofs/stream-chat/**` with none of the excluded files: no `requirements*`, lockfile, `package.json`, `package-lock.json`, `.npmrc`, `pyproject` dependency or chat baseline change).
2. Classification with the trusted policy extracted from `origin/main` (`0f45e64`) outside the worktree and run as `python3 -I …/change_scope.py --base b04306d67c79d3a2ff1981d6bc3c65ca0de24bd1 --head <head> --merge-base`: `{"full": true, "reason": "behavior-or-empty", …}`, full scope as expected (the policy accepts full SHAs only; a short SHA answers `missing-or-invalid-comparison`).
3. Installs: the pinned toolchain (`scripts/bootstrap-toolchain.sh`: node 24.19.0, npm 11.9.0, Python 3.12.14), `python3.12 -m venv .venv`, `pip install --require-hashes -r requirements-dev.lock` and `pip check`, `npm ci --ignore-scripts`, with the proxy and CA variables by reference; `npm audit`: 0 vulnerabilities. No dependency file changed.
4. Offline checks under `env -i` without `STREAM_*`: 503 tests OK (393 at the start; 426 after step 1; 496 after step 2; 501 at `2ff6807`; 502 at `93390ce`; 503 at `ad89753`); Ruff "All checks passed!" and "55 files already formatted"; mypy "Success: no issues found in 53 source files" (corrected in P06.1-C4; the I2b review's nit 5: this line said 55, the Ruff format count; mypy checks 53 source files, as step 2's line says); `node --check` OK for `runner.cjs`, `product-op.cjs`, `error-info.cjs`, `request-log.cjs`; `checks/run_plan.py` fits with an empty ledger (`all_fit: true`, 18 of 20 users, 8 of 30 channels) and, with this checkout's ledger after the runs, reports "DOES NOT FIT" as designed (deviations).
5. Fix reversals (`checks/fix_reversals.py`, in a scratch copy): 242 at the start; 274 at `bca64eb` (03:04:08 to 03:22:04); 341 at `2ff6807` (04:45:07 to 05:12:53); 342 at `93390ce` (05:28:40 to 05:56:31) and 342 at `ad89753` (06:01:01 to 06:29:10); "not demonstrated: 0" every time; the reasons of the I2b entries read.
6. The pin test (`services/api`, `python3.12 -m unittest tests.test_toolchain_pins`): 3 tests OK at `bca64eb`, the only commit that touches the workflow, and again at the final head.
7. `git diff b04306d HEAD -- .github/`: one file, `foundation.yml`, +34 −2: the new job `proof` and the gate's `needs` entry and tuple entry, nothing else.
8. Secret scan: the whole diff `b04306d..HEAD` and every live log and results file (15 logs, 12 `.work` files) grep-counted for the secret, the API key and JWT-shaped strings (`eyJ…`): 0 and 0 for the secret and the key everywhere; the one JWT-shaped string in the diff is the fabricated value `eyJhbGciOiJIUzI1NiJ9.abcdefghijklMNOP.sig` in `tests/test_redaction.py`, a redaction test's input, not a token; none in any live output. No output held a token or the secret.
9. Live checks: every run's preflight found the one dashboard user and no other data (`configuration_problems: []`, calls, feeds and activities 0 before each run); every run's cleanup completed with every remaining list empty and `post_run_problems: []`; after the last run `verify-clean` and both dry runs (commands 13 to 15) show no leftover and no difference.

### Deviations and limits

- **The reserve rerun went to run V1, before the lockdown.** The first run V1 (`p061i1-0927051807`, 05:18:05 to 05:18:30 UTC, exit 0, cleanup complete) left eight Feeds cases INCONCLUSIVE: `FD-feed`'s control undo hard-deleted A's feed, and Stream does not recreate a deleted feed ID (`GetOrCreateFeed failed with error: "feed with id: … has been deleted"`, even after `hard_delete=true`), so every later fixture of A's feed got 404 code 16. Its Video rows and its two Feeds HOLDS are the same as the rerun's. The fix (`93390ce`: the replay leaves A's feed in place, recorded, for cleanup; the fake models the tombstone) has a failing test and a reversal. The same commit also changed FD-feed's step body: its custom note no longer carries the Feeds marker (`{fd_text}` became `feed of {A}`), so FD-read's disclosure question stays about A's activity, not A's feed (corrected in P06.1-C4; the I2b review's nit 9: this bullet named only the removed undo). The whole set (342) was demonstrated at that head before the rerun. The prompt allows one reserve rerun; it was spent on V1 so that every Feeds case has its before-lockdown row, and run V2 therefore had no rerun available. The offline fakes had not modelled the tombstone; this is the one harness defect the live work found.
- **Two fix commits between live commands**, each followed by the offline checks and the whole reversal set at the new head (about 28 minutes each) before the next live command that changes anything, as section 5 requires: `93390ce` (above) and `ad89753` (the lockdown stamp). The stamp commit also moved the fake products' default configuration to the lockdown target: with `products.LOCKDOWN_APPLIED` set, every run's preflight compares the products, and the fake's pre-lockdown grants would otherwise have read as drift in 40 offline tests. The fake's capability knob (`allowed`) is separate from its grants, so the before-lockdown verdict tests are unchanged; the tests of the plan and of drift put the pre-lockdown model back explicitly.
- **`checks/run_plan.py` mid-session.** The script adds this checkout's usage ledger to the whole plan, as a check before any live call; after run 1 and run V1 it reports "DOES NOT FIT" (27 users: the ledger's 9 plus the plan's 18 again). With an empty ledger, CI's condition, it fits (`all_fit: true`); the remaining live runs fit the caps (11 users used before run V2, 13 after, of 20). No live run was started against the guardrails: the harness's own ledger enforces the caps in every run.
- **Fifteen commands in the live table** against the thirteen that section 5 of the I2b prompt names, the reserve rerun included: the two beyond them are command 3, a scoped dry run before run 1 besides the one right before the apply (command 10), and command 8, `record-products-baseline`, which made no network call. The reserve rerun (command 9) and the closing checks (commands 13 to 15: `verify-clean` and both dry runs) are in the plan (corrected in P06.1-C4; the I2b review's nit 6: this bullet said "Fourteen live commands against the plan's eleven", which no count gives).
- **F9-thread is INCONCLUSIVE by design of the configuration**, not by a defect: `replies` is off in `glow-match`, so no thread exists and the member's own read is 404 too. The row is no evidence either way; the F9 read of a thread outside the match is covered by the grants (no `read-channel` outside the match) and the I2a F9 reads that HOLD.
- **The manager branch's head** was one Markdown-only commit ahead of `b04306d` at session start; the prompt was read at `b04306d`, as the prompt directs.
- **Limits of the Video and Feeds results.** The runner holds a chat WebSocket only: a call's `custom` event and `call.member_added` reaching the other member were not observed, only the REST answers. The requests went to the chat host, as the server SDK sends them; the Video and Feeds hosts were not exercised. Which grant governs `QueryActivities`, `AddActivity` for a feed's creator and `UpdateActivity` for an activity's owner is not documented and not determined by the proof; the fake products model them as capabilities, not grants. A call's member's remaining grants (join, send audio and video, recording, broadcasting) were not exercised: the deny-list refuses them, and none was needed to show the member's reach.
- **`VD-query` after the lockdown is INCONCLUSIVE, not HOLDS**, because the refusal's code is 102, not 17, and the quality rule attributes only a permission error to the token; its message says access was denied and, in the same breath, that calls match. Before the lockdown the same query succeeded and disclosed. **`FD-read` after the lockdown is INCONCLUSIVE** because the owner's own read is refused too: no positive control, though the refusal is attributable (code 17, `ReadFeed`).

### What P06.2 and the delta review must know

- **The lockdown is applied to application 1729640** (27 September 2026, 05:58:31 UTC) and recorded in the harness (`products.LOCKDOWN_APPLIED`): from `ad89753` on, every run's preflight, every end of run and every dry-run `configure` compares Video and Feeds with the target, and `restore` does not undo it (the baseline holds the grants; returning them is the same `PUT`s with the recorded grants, which no command sends). The development application is not a production control (DM-02 B7 (c)); the production plan is section 5 of the architecture document.
- **What a user token could do before it** (run V1: 16 of 18 cases) is the reason the production plan must carry the Video and Feeds part; **what it can still do after it** (run V2): creating calls, reading and querying other users' calls, reading other users' feeds, following, commenting, reacting and updating a feed are refused; a call's member or creator and a feed's creator keep what their roles grant, and any user token can still query another user's activities and read their text (`FD-query`). For Glow the last two are closed only by the design constraint that the server creates no call, feed or activity for a user; the activities query is open for Nathan's decision (ask Stream, or test the remaining roles).
- **Chat, under the corrected rules (run 1):** removal and deactivation MEET the history policy under the 404 code 16 rule with its three conditions; the existence oracles stand (`EO-channel` also through `sync`, by shape; `EO-message`); no record holds the `sync` pair's two normalized answers, which stayed in I2b's local results file, not kept, so that `sync` is an oracle rests on the one observation recorded above (corrected in P06.1-C4; the I2b review's nit 10); `F9-sync` HOLDS (filtered); `F9-thread` is INCONCLUSIVE because no thread can exist with `replies` off.
- **For the delta review:** the review's items are the I2b diff against `b04306d` (the commits `bca64eb`, `a1880fb`, `2ff6807`, `1137786`, `93390ce`, `ad89753` and the records commit); the two live-found harness changes (`93390ce`, `ad89753`) came after the first live command, each with a failing test, a reversal and the whole set demonstrated at its head; the fake products now start at the lockdown target; the architecture document's claims are all "not yet" reviewed for I2b's runs.
- **P06.2 constraints** are in the architecture document, section 8; nothing here decides the design.

### Manager verification of I2b (App Manager 4, 27 September 2026)

App Manager 4 checked the relayed report against the pushed branch. The manager makes no call to Stream. The live results therefore rest on this record and on the code that produced them, and I2b's exact-head review checks both.

- **Identity:**
  - branch `claude/confident-brown-baykju`, head `0a0512c1fa95c1c55546eff57ba4d68f79325b3a`, tree `fdb431aaade15fb027441d7ea410fa568575eddc`; seven commits on the start `b04306d`, in the report's order (`bca64eb`, `a1880fb`, `2ff6807`, `1137786`, `93390ce`, `ad89753`, `0a0512c`), one merge base with the start; code head `ad89753`; the last commit changes only Markdown;
  - 41 files, +11,719 and −175: 38 under `proofs/stream-chat/` (7 new: `products.py`, `client/product-op.cjs`, the products baseline, `tests/fake_products.py`, `tests/test_products.py`, `tests/test_product_cases.py`, and the architecture document outside it), `.github/workflows/foundation.yml`, `docs/architecture/chat-provider-permissions.md` and this record. Every path is owned; no dependency file, lock, `.npmrc`, `pyproject.toml` dependency or committed chat baseline changed; every file under `proofs/stream-chat/` has mode 100644, and there is no symlink; `git diff --check` is clean;
  - the ten sections the I2b prompt protects are byte-identical to `b04306d`. The two nit 6 sentences are corrected in place and marked "(corrected in P06.1-I2b; the I2a review's nit 6)".
- **The workflow diff** (`git diff b04306d 0a0512c -- .github/`): one file, +34 −2: the job `proof` ("Stream proof checks") and the gate's `needs` and tuple entries, nothing else. The job has the other application jobs' condition, action pins and `persist-credentials: false`; `working-directory: proofs/stream-chat`; `timeout-minutes: 10`; `python-version: '3.12.14'`; `node-version: '24.19.0'` with `package-manager-cache: false`; one `npm install --global npm@11.9.0` in the other jobs' form; no `secrets.*` and no `env:`; and it runs the README's installs and offline checks. The pin test passed in the manager's export of `0a0512c`: 3 tests, OK.
- **Classification:** the trusted policy from `main` (`0f45e64`, sha256 `dec69a26…`), run outside the tree with `python3 -I` and full SHAs: `behavior-or-empty`, full scope, for `b04306d..0a0512c` and for `main..0a0512c`; one merge base.
- **Offline re-run,** in a scratch export of `0a0512c`, in clean processes without any `STREAM_*` variable, installs with the proxy and CA variables by reference: `pip install --require-hashes -r requirements-dev.lock` and `pip check` ("No broken requirements found."); `npm ci --ignore-scripts` ("found 0 vulnerabilities"). Unit tests: `Ran 503 tests`, `OK`. Ruff check: "All checks passed!"; Ruff format: "55 files already formatted"; mypy: "Success: no issues found in 53 source files"; `node --check` on the four `.cjs` files: OK; `checks/run_plan.py` with an empty ledger: "run plan: fits". `checks/fix_reversals.py`: "reversals: 342, not demonstrated: 0", exit 0, 07:55:50 to 08:14:33 UTC; every row OK, 396 reversals failed on an assertion and 47 on the error their reverted fix causes, none through a syntax, import or name error; the 100 I2b entries among them.
- **Secret scan** of the whole diff (707,890 bytes): 0 JWT-shaped strings apart from the fabricated redaction-test input the report names, 0 email addresses, 0 private-key blocks, 0 secret assignments, and 0 occurrences of the application's API key. The committed products baseline holds `app_id`, `video` and `feeds` (call types, feed visibilities and feed groups with their grants and settings): no user, no data, no email address.
- **Code read,** at `0a0512c`: the deny-list and allowlist in `client/product-op.cjs` and `glow_stream_proof/products.py` (the same words and fields in both, the deny-list checked first); the guard's `video` and `feeds` families (`guard.py`: `products.denied` first, a configuration write only inside `ConfigureScope` and only with the lockdown's body, then the owned-object rules); `_configure_products` in `cli.py` (a plan filtered to the named products, the refusal while chat does not verify, the refusal of a path that is not one of the two configuration writes, the re-read and verification); `configuration.verify` comparing the products only from `products.LOCKDOWN_APPLIED` on; `usage.product_unavailable_wording` and the `upgrade`-only exemption; `checks/run_plan.py` adding the session's ledger to the whole plan.
- **Hosted CI on I2b's branch:** Foundation runs 305 to 310 on its seven commits all succeeded. On `ad89753` (run [36298830899](https://github.com/amthorn78/glow-dating-app/actions/runs/36298830899)) the manager read the jobs: "Stream proof checks" ran, not skipped, every step success (installs, `pip check`, `npm ci`, the tests under `env -i`, Ruff, format, mypy, `node --check`, `run_plan.py`), and the gate passed with `proof` in its list. Run 310 on `0a0512c` was ordinary documentation (the records commit), so its application jobs were skipped and its gate passed.
- **The record's counts:** the live-command table's 15 rows and the usage after the last run (13 users, 4 channels, 560 calls, peak 4) are consistent with the runs' figures; run V1's 16 FAIL and 2 HOLDS, run V2's 9 HOLDS, 7 FAIL and 2 INCONCLUSIVE, and run 1's eight verdicts add up to their case counts.
- **Not re-run by the manager:** the session's live commands (they cannot be); its independent check; its own reversal runs (the manager's run above is on the final head).
- **Integration:** merged into the manager branch as `55b22387e6478e4b7c8d58480108e4c7341c4564`. Against its first parent (`c6e9bf4`) the merge brings exactly I2b's 41 files; against I2b's head it differs only in the manager's records since `b04306d` (the handoff, the mistakes log, the register, the manager workflow and the start prompt).
- **Hosted CI on `55b2238`:** the merge was pushed with the records commit `84b2d6f`, whose code is the merge's. Push run [36305057769](https://github.com/amthorn78/glow-dating-app/actions/runs/36305057769) and PR run [36305061337](https://github.com/amthorn78/glow-dating-app/actions/runs/36305061337) on `84b2d6f` each ran all seven jobs: Change scope, the five application jobs ("Stream proof checks" ran, not skipped, every step success) and the gate, all success; the rendered suite passed. The classification for the push run compared against the previous push, `c6e9bf4`, so it covered I2b's code.

#### Dispositions

- **I2b is verified and integrated** at `55b2238`. Its results are recorded above and in the architecture document; each is "not yet" reviewed until I2b's exact-head review confirms it (DM-01 P4).
- **The deviations are accepted:**
  - the reserve rerun spent on run V1, after the fix of the harness defect the first attempt exposed (`93390ce`), so that every Feeds case has its before-lockdown row; run V2 then had no rerun and needed none;
  - two code commits between live commands (`93390ce`, `ad89753`), each followed by the offline checks and the whole reversal set before the next live command that changes anything, as section 5 of the prompt requires;
  - `checks/run_plan.py` reporting "DOES NOT FIT" mid-session, because it adds the ledger to the whole plan again. The count before any live call fitted, and the harness's own ledger enforced the caps in every run (13 of 20 users after the last). The script's mid-session reading is misleading, not wrong about the caps; the review assesses it, and a later offline pass may make it count only what remains;
  - fifteen commands in the live table, against the thirteen that section 5 of the prompt names, the reserve rerun included: command 3, a scoped dry run before run 1 besides the one right before the apply, and command 8, `record-products-baseline`, which made no network call (corrected by App Manager 5; the I2b review's nit 6; AM4-06);
  - F9-thread INCONCLUSIVE with replies off; VD-query (code 102) and FD-read (no successful control) INCONCLUSIVE after the lockdown, under the matrix quality rule.
- **The lockdown stands** on application 1729640 for the rest of P06.1, as the brief says; Nathan decides at P06.1's close whether the development application stays locked down (likely) or is restored, and the products' baseline records what restoring would send.
- **Open, not decided here:** the activities query returns another user's activities after the lockdown, and a call's member or a feed's creator keeps what their resource roles grant. For Glow both are closed by the design constraint the architecture document states (the server creates no call, feed or activity for a user). Whether to ask Stream which grant governs the activities query, or to test the remaining roles, is a question the manager puts to the Dev Manager with the close-out consultation (OD-32), not to Nathan now.
- **Manager-owned follow-ups from DM-05:** the CI policy's job names and counts are updated in this batch (finding 4 (c)); ADR 0003's conditions and "Revisit when" are updated after I2b's review (finding 5 (b)).
- **I2b's exact-head review is next,** offline and scoped to I2b's change, at `55b2238`.

### Exact-head review of I2b (27 September 2026)

Nathan ran the review session on Fable 5.1 at max, from revision 3 of the [review prompt](../../ephemeral/2026-09-27-p06-1-i2b-review-prompt.md) (records commit `edbe592`), and relayed its report to App Manager 5. The session committed and pushed nothing, and made no Stream call.

- **Verdict: approve.** I2b's harness, records and architecture document are sound, and no recorded result changes. The I2a review's items, DM-05's conditions and the independent check's findings are confirmed fixed or applied. Both design decisions that rest on I2b's live results are sound: removal and deactivation meet the history policy under the 404 code 16 rule, and the record of what a user token can and cannot do in Video and Feeds before and after the lockdown. The activities query stays open, as recorded. The reviewer agrees with all six of the manager's dispositions.
- **Two should-fix findings and eight nits remain.** Finding 1 falls, narrowly, in the class that gets an offline correction pass before P06.1 closes: the runner's generic `call` op can reach Video and Feeds endpoints without the product op's allowlist or deny-list. No case uses that path, and no live run remains. Finding 2: the lockdown's verification and its record cover only the client roles' grants.

#### The report, as relayed

The session's notes before its report, verbatim:

> I'll start with the environment check (names only), then the start gate and classifications, then read the records and the diff before running the offline checks.
>
> Environment is clean: none of the six variables is set, and the toolchain matches the expected pins. Now the start gate.
>
> Start gate passes on every line. Now the three classifications and the non-Markdown scope check.
>
> All three classifications matched expectations. Now I'll pull the file list and sizes, then read the prompt, DM-05, and the records in parallel.
>
> All 41 files are mode 100644 and there are no symlinks. Now the reading: the I2b prompt, DM-05, and the manager README entry in parallel.
>
> The prompt and DM-05 outputs were saved to files. I'll read them in full now.
>
> I've got the prompt and DM-05. Now I'll pull the remaining independent records in one batch: the DM-05 disposition section, the evidence record's I2a/I2b reviews, the architecture document, harness README, ADR 0003, the workflow, the pin test, and the manager's verification at `edbe592`.
>
> I have several saved outputs to read in full, plus the manager's verification of I2b and the brief sections at `edbe592`. None depends on another, so I'll read them all now.
>
> I'll pull the rest of the README, the brief at edbe592, and confirm the install directories are ignored—all at once since they're independent—then kick off the installs in the background.
>
> I've confirmed the install directories are already covered by the root ignore file. I'll now kick off the installs in the background while starting to review the code diff, prioritizing the highest-risk files: the product op, the products module, and the guard.
>
> The product op and guard tables check out on their own. Now I'll pull in the runner's call op, the server hook's guard installation, and the CLI's scoped configure/probe/baseline wiring in parallel, since these can be read independently.
>
> The installs finished. Before starting the offline checks I'll read the install log and confirm where the fix-reversal script puts its scratch copy, so nothing lands inside the repository.
>
> Installs are clean with no changes to the tree. I'll now pull the reversal script's copy logic, check on the offline background checks, and review diffs for the verdict-bearing modules (mechanisms, i2a, matrix, proof_run, run_plan), since these are independent and can be requested together.
>
> Got the diffs for mechanisms, i2a, matrix, and run_plan. Now I'll read the full proof_run diff, which contains the case loop, disclosure rule, product-finding verdict, fixtures, and cleanup.
>
> I've read the verdict-bearing code. Next I'll kick off the fix-reversal run in the background and gather the remaining independent pieces: whitespace/secret scans, the protected-section comparison, baseline client-role grants against the nine recorded PUTs, F9-sync/F9-thread leak terms, `_case_verdict`/`step`/`judge_dimensions` and the `after_detail` caller, the `_CHARGE_WORDS` regex, the client bridge's `call`/`product` handling, and the GitHub tool schema for the hosted CI check.
>
> The offline checks are done. I'll review their log, then re-run the three misfired reads (the `step` method, F9-thread's leak terms, and the client bridge's `send`), and split out the I2a review section's diff into I2b's change versus the manager's.
>
> Everything offline checks out clean (tests, lint, formatting, mypy, node checks, run plan, pin test), and the protected-section diff is just a harmless blank-line separator I2b added. The three failed reads were due to a stale relative path after the working directory changed—I'll redo them with absolute paths and also pull hosted CI, the I2b test files, and the reversal table.
>
> Everything's clean so far—environment, installs, offline checks, and hosted CI all pass with "Stream proof checks" actually running. The fix-reversal job is running in the background while I read I2b's tests and reversal table using absolute paths.
>
> Reading the saved test outputs and the reversal table next, plus the two live-found fix commits in isolation, the F9-thread case, and the family channel naming. All independent, so one batch.
>
> I still need several independent checks: the reversal run's result, two offline probes on the deny-list and case-sensitive key matching, a diff scan for the API key value, verification that no matrix step reaches client request methods, the `ws_dimension`/`_guard_refusal` code paths, and a final tree-state check. Since these are all independent, I'll run them together.
>
> Probe 1 was inconclusive since the SDK blocked the call locally before hitting any request path—I'll rerun it with a development-token REST user to distinguish a budget refusal from an op refusal. Probe 2 confirmed differently cased keys pass both tables; I'll also redo the other reads with absolute paths since they failed due to the working directory shifting again.
>
> The bypass probe is conclusive: with a REST user set, the generic `call` op reached the request interceptor and was stopped only by the budget, while the `product` op on the same path was refused by the deny-list. Still pending: the reversal run, a harness tree check against I2b's code head, verifying the `configure`/`restore` plans reference no product path, and hosted CI on `ad89753`.
>
> The reversal run is about a third done and will notify me when finished. Meanwhile I'll check the missing run-1 line in the run plan and verify that the CI policy at the records commit names the fifth job as the manager's disposition indicates.
>
> The fix-reversal run is about a third done and should finish in roughly half an hour. Everything else offline is complete, so I'll just wait for that run's summary rather than poll it.
>
> All checks are done except the fix-reversal run, which is still in progress (~half an hour left). I'll wait for its summary line to appear and then finish writing the report with the exact result.
>
> I'll wait for the reversal run to finish, but in the meantime I'll check whether any current no-leak case could vacuously satisfy the disclosure rule, and pull F9-thread's definition, which my earlier grep missed since it's generated in a loop.
>
> I need to pull the full definitions of R7a, R7b, R8a, and R8b since my grep cut off their leak terms, and check whether RT1 and S15 route through the new disclosure code at all—both quick independent reads while the reversal run continues in the background.
>
> All findings and checks are settled, including confirming the disclosure-rule question stays closed (no no-leak case has every leak term satisfied by its own request). I'm just waiting on the fix-reversal run results before finalizing the report.
>
> Nothing further can be requested until the reversal run finishes: at 12:44 UTC it stood at 140 of 342 with no failure so far, so about twenty-five minutes remain. Both the run itself and the waiter on its summary line will notify me; I'll write the report as soon as the result is in.
>
> The reversal run has finished. I'll read its summary, break down the failure reasons, list I2b's entries, and confirm the tree is unchanged.
>
> All 342 reversals check out against the manager's figures (396 assertion failures, 47 errors, 3 by-design aborts, no "not demonstrated" cases). Next, I'll review each of I2b's 100 entries' failure reasons to confirm none stem from loading or naming errors.

The report ("Review of P06.1-I2b at `55b2238`"; its headings are moved down to fit this record):

**Prompt received:** revision 3, from commit `edbe5927d0a6279f4fea591dd03623a1b95722fe`.

**Head reviewed:** `git rev-parse HEAD` printed `55b22387e6478e4b7c8d58480108e4c7341c4564`. `HEAD^2` is `0a0512c1fa95c1c55546eff57ba4d68f79325b3a`. One merge base, `0f45e648099b415217938c25d7369164c0101def`. The ancestor check printed "records build on the head". The diff stat is 41 files, 11719 insertions, 175 deletions. The harness at the head is identical to I2b's code head `ad89753` outside Markdown.

**Environment:** none of `DATABASE_URL`, `HD_API_KEY`, `GEO_API_KEY`, `STREAM_APP_ID`, `STREAM_API_KEY`, `STREAM_API_SECRET` is present. node v24.19.0, npm 11.9.0, npx 11.9.0 and Python 3.12.14, all from `/root/.local/bin`.

| Classification (trusted `main` policy, sha256 `dec69a26…`, `python3 -I`, outside the tree) | Output |
|---|---|
| `main` → head | `{"full": true, "reason": "behavior-or-empty"}`, 129 paths |
| `6a51dae` → head | `{"full": true, "reason": "behavior-or-empty"}`, 55 paths; the filter for non-Markdown files outside `proofs/stream-chat/` and the workflow printed nothing |
| head → `edbe592` | `{"full": false, "reason": "ordinary-docs-only"}`, 11 paths |

**Verdict: approve.** I2b's harness, records and architecture document are sound, and no recorded result changes. There is no blocking finding. Two should-fix findings and eight nits remain. Finding 1 falls, narrowly, in the class that gets an offline correction pass before P06.1 closes: the runner has a second path to Video and Feeds endpoints that skips the deny-list. It is a few lines to close, no case uses it, and no live run remains in P06.1. Finding 2 and the nits go to the final delta review and the records. Both design decisions that rest on I2b's results are sound.

##### Findings, most severe first

Paths are under `proofs/stream-chat/` unless said otherwise.

**1. Should fix. The runner's generic `call` op reaches Video and Feeds endpoints without the product op's allowlist or deny-list.**
- Where: `client/runner.cjs:266` to `:279`, the `call` op, which invokes any method of the SDK client with any arguments; `glow_stream_proof/client_bridge.py:260`, which passes any method name; `glow_stream_proof/matrix.py:2053`, where `validate` checks `product` steps only.
- Scenario, reproduced offline with a zero request budget and an unreachable proxy, so nothing left the machine: after a REST user was set, a `call` on the client's `post` to the chat host's `/api/v2/video/call/default/x/join` with `ring: true` reached the SDK's request interceptor and was stopped only by the budget, error kind `budget`. The `product` op on the same path was refused by the deny-list, kind `refused`. With a budget, the request would have been sent.
- What holds: no case in the matrix uses this path. Every product case is a `product` step, which `validate` checks against the op, and the 18 live rows record the op's requests. The README's claim that the op is how a case sends a product request is true of the cases, not of the runner.
- Fix: check the deny-list and allowlist inside the request interceptor for any URL whose path starts `/api/v2/video/` or `/api/v2/feeds/`, whatever op sent it; or refuse `call` on the client for its generic request methods. Add a `validate` rule, a test that drives the real runner, and a reversal.
- Class: yes, narrowly. It lets a harness-authored request escape the deny-list. The exposure before P06.1 closes is nil, since no live run remains; the rule still routes it to the correction pass.

**2. Should fix. The lockdown's verification and its record cover the client roles' grants only.**
- Where: `glow_stream_proof/products.py:351` to `:370`, `verify`, which flags a client role's non-empty grants and an unverified read and nothing else; `glow_stream_proof/cli.py:259` to `:287`, where the full re-read is compared by that `verify` alone and the record keeps the client roles' grants alone.
- Scenario: had a `PUT` reset a call type's settings or a resource role's grants, the re-read would still have printed "differences after: []" and the record would hold nothing of it. Later drift in `admin`, `call_member` or a setting goes unseen the same way. The README sentence "that Stream changes only the roles named is documented and verified by the re-read after the apply, not assumed" overstates what was verified: the client roles read `[]`; the other roles and the settings were not compared with the baseline.
- What holds: the guard's `is_lockdown_body` proves each body was `grants` alone, naming client roles with `[]`. A change elsewhere could only come from Stream departing from its documented partial update. The nine `PUT`s are exactly the scopes where the committed baseline shows a client role with a grant, and the grant counts in the architecture document's section 5 match the baseline.
- Fix: compare every non-client role's grants and each call type's settings with the committed products baseline, as the chat check does with its baseline; keep the full after-state in the record; correct the README sentence. A read-only `baseline` at P06.1's close, compared with the committed products baseline, would show what the nine `PUT`s left. That is a live command and the manager's call.
- Class: none. No verdict rests on it, and the scoped configure could not have sent anything outside the two families.

**3. Nit. Deny-list keys are matched case-sensitively.**
- Where: `client/product-op.cjs:57` to `:58`; `glow_stream_proof/products.py:123` to `:125`.
- Scenario, reproduced: `Ring: true`, `NOTIFY: true` and `video: "True"` pass both tables. Go's JSON decoder, which Stream's API uses, matches field names case-insensitively, so such a key may be honoured. Only harness code could send it, and `validate` would not catch it.
- Fix: compare lowercased keys and values. Class: the deny-list class in principle, but it needs a deliberately miscased key in a case definition.

**4. Nit. The disclosure rule can HOLD (filtered) with nothing scanned.**
- Where: `glow_stream_proof/proof_run.py:1784` to `:1787`, `_disclosure`, where the scanned list may be empty.
- Scenario: a future no-leak case whose every leak term is carried by its own request would HOLD (filtered) when its control found the terms. No current case is so: R3, R4 and R5 keep three of four terms; R7a and R7b keep the message ID; R8a keeps the names; R8b keeps all; F9-sync keeps three; the four product no-leak cases keep all.
- Fix: INCONCLUSIVE when nothing is left to scan. Class: a false HOLDS in principle only; no case can trigger it.

**5. Nit, records.** The I2b section's "Checks" item 4 gives mypy "55 source files". The head answers 53, as I2b's own step-2 line and the manager's run say.

**6. Nit, records.** The deviations say "Fourteen live commands against the plan's eleven"; the table has 15 rows, and the manager's verification and the brief say fifteen. Row 8 makes no network call, which explains fourteen against fifteen; "eleven" is not derivable from the prompt's section 5.

**7. Nit, records, architecture document.** Section 3's existence-oracle row attributes to ADR 0003's consequences that channel and message IDs are random, opaque and never shown. The ADR says that of user IDs. The document should state it as its own design constraint, as DM-05's finding 5 (a) allows, and mark it open for P06.2 as it does for channel naming.

**8. Nit.** A non-2xx `PUT` mid-plan leaves no record: `cli.py:65` to `:84` raises on the first failure, and the re-read and the record at `:258` to `:287` come after. Not exercised live; the nine answers were 201. Fix: re-read and write the record in a `finally`.

**9. Nit, records.** Commit `93390ce` also changed FD-feed's step body, whose custom note no longer carries the Feeds marker; the deviation bullet describes only the removed undo. The commit message says both.

**10. Nit, records.** The `sync` pair's FAIL is recorded as "a list of two entries against one" without naming the list or its entries; the normalized shapes live only in I2b's local work files. The architecture document's "sync is an oracle too" rests on that one observation. The record should quote the two normalized shapes.

##### Confirmations and assessments

**The I2a review's items, DM-05's conditions and the independent check:** all confirmed fixed or applied at the head.

| Item | Where confirmed |
|---|---|
| I2a finding 1 | `mechanisms.py` `stepping`, `collect_after`, `apply`, `after_apply`; `KeptStepsTest`, three tests; reversals "I2b finding 1" ×3 fail on `'INCONCLUSIVE' != 'DOES NOT MEET …'` |
| I2a finding 2 | `i2a.py` `shape`, `_normal`, `normalized`; `OracleTest`; both normalized answers in every pair's row |
| I2a nit 3, eight tests | margin on every dimension, listener, retention, oracle control, 5xx pair, 5xx write put back, transport attempts, setting type; none left; eight reversals |
| I2a nit 4 | `guard.py:394`, every mutating `messages/{id}` path; `RefusalTest` and the real-hook test; S3a HOLDS live with its replay 201 |
| I2a nit 5 | `EveryOpTest`: the real runner answers every op, `product` included, nothing sent |
| I2a nit 6 | two sentences corrected in place, marked; the third hunk of I2b's record change |
| DM-05 finding 1 | `_configure_products`: a difference, chat verification, refusals in code, `ConfigureScope`, re-read; `ScopedConfigureTest`, eight tests and five reversals |
| DM-05 finding 2 | runs 1, V1 and V2 separate; `probe-products`; `unavailable_answer` and the `upgrade`-only exemption; cleanup proceeds |
| DM-05 finding 3 | `product-op.cjs` and `products.py` tables, deny-list first; the guard's `_product`; `AllowlistTest` drives the JS file with node over 61 rows and requires the same reason; every object has a delete |
| DM-05 finding 4 | the workflow, below; the pin test OK |
| DM-05 finding 5 | the architecture document's sections 3 and 4 |
| DM-05 finding 6 | `checks/run_plan.py` counts run 1, V1, V2 and the largest in reserve; S3a live |
| Independent check 1 to 6 | `undo_verdict` before the replay; `events(into=…)` with the `except BaseException` keep; subject and object words, 404 as an object, listings not verified stop preflight; `is_lockdown_body`; the chat-only gate; the two tables agree on `"true"` and on order; reversals "I2b check 1" to "check 6" |

**The design decisions that rest on I2b's results.**

- **Removal and deactivation MEET under the 404 code 16 rule: sound.** `missing_404` returns ended only on a 404 with code 16, only for the affected member after a removal or deactivation, only with the other member's identical request collected and successful after the mechanism, and only with a message naming the membership or the user; `dimension` first requires the same member's success before. A missing channel fails the second condition, a malformed request the first and second, a harness error is no response. Given the recorded answers, `policy_verdict` must give MEETS. The residual is the record itself, which cannot be re-run.
- **What a user token could do before the lockdown and what remains: sound.** Every FAIL in run V1 is the client's 2xx or B reading A's data with the terms scanned outside what its request carried. Every HOLDS in run V2 is a 403 code 17 with the server's 2xx control or A's own read finding the data; `refused_verdict` and `no_leak_verdict` allow nothing else. The seven FAILs after the lockdown are 2xx answers. Run V2's preflight compared the products under the recorded stamp, so the client roles read `[]` and the `.app` grants empty when those answers came.
- **The activities query left open: sound as recorded.** A 201 with A's text and activity ID to B after the lockdown, with no grant in the plan governing it.

**The disclosure rule, an assessment note.** The rule filters an echoed identifier even where the echo is an existence signal, as in R8a's queried IDs or a cid in `inaccessible_cids`. The existence-oracle cases carry that question, and EO-channel's `sync` pair caught it. The rule and the cases together are sound; the README could say that the oracle cases hold the existence question.

**The manager's dispositions.** I agree with all six.

- **The reserve rerun spent on run V1:** agree. The first attempt's eight INCONCLUSIVEs were a harness defect, the rerun gave every Feeds case its before row, and run V2 completed without a rerun.
- **Two fix commits between live commands:** agree. Each has a failing test and a reversal, the whole set was demonstrated at each head, and every live command names its committed head. Commit `93390ce` also changed FD-feed's step body, nit 9.
- **`checks/run_plan.py` reading "DOES NOT FIT" mid-session:** agree that it is misleading and not wrong about the caps. The script adds the ledger to the whole plan again by design. The delta review can make it count only what remains.
- **F9-thread INCONCLUSIVE:** agree. With replies off no thread exists, the control failed, and the reads outside the match are covered by the grants.
- **VD-query and FD-read INCONCLUSIVE after the lockdown:** agree. Code 102 is not attributable, and FD-read's control was refused. VD-query's message is itself an existence signal, which the architecture document records.
- **The activities query open, not decided:** agree, including putting it to the Dev Manager at close-out.

**The workflow.** `git diff HEAD^1 HEAD -- .github/` is exactly the job `proof`, "Stream proof checks", plus the gate's `needs` entry and its Python tuple entry. The job's condition is the other application jobs' condition, its action pins and `persist-credentials: false` are the same, `python-version: '3.12.14'`, `node-version: '24.19.0'` with `package-manager-cache: false`, one `npm install --global npm@11.9.0` right after setup-node with the workspace as its working directory, `timeout-minutes: 10`, no `secrets.*`, no `env:`, and it runs the README's installs and offline checks plus `checks/run_plan.py`. PR run 36305061337 on `84b2d6f`, a Markdown-only records commit whose code is the head's: all seven jobs succeeded; "Stream proof checks" ran, not skipped, every step success, the tests in 38 seconds; the gate succeeded. Push run 36298830899 on the code head `ad89753` shows the same. The gate's Python list at the head includes `proof`.

**Areas reviewed with no findings.**
- **The guard's Video and Feeds scope:** deny-list first, a configuration write only in `ConfigureScope` and only with the lockdown's body, a call type's creation or deletion and a feed group change refused everywhere, deletes only of run-owned objects, every named user the run's, the queries reads; the real hook refuses typed and raw calls alike before counting; the run's scope never allows product configuration; `cleanup --apply` owns calls and feeds by prefix only.
- **The scoped configure:** the plan is a difference of `PUT`s naming only client roles with `[]`; nothing for an unavailable product or a scope at the target; `--apply` refuses on chat problems, on a planned path outside the two families, and on an unknown product; the general `configure` and `restore` plans reference no product path.
- **The applied plan against the baseline:** nine scopes, roles and grant counts match the record and section 5 exactly; `default` lists no `anonymous` and `audio_room` and `livestream` no `guest`, as the document says.
- **The product-finding rule and signals:** 402, code 99 and every other charge word still stop; a fixture's or a case's unavailable answer ends only that product's cases; chat rows are never touched; `NOT AVAILABLE` is neither kept when interrupted nor a pass; every new server path goes through the hook and cleanup is skipped after any recorded signal.
- **Fixtures, tracking, cleanup, preflight and `verify-clean`:** each object recorded from the answer that created it, `undo_once`, FD-feed's feed kept for cleanup, deletes accepted as 2xx or 404 with tasks completed, the Feeds data delete, preflight refusing foreign objects and unverified listings, the poll listing as each run user with each recorded poll read back.
- **The oracle and the interruption fixes:** shape without `duration`; `ws_dimension` cannot give ended when a window was not collected or no probe was accepted; `step` sends nothing.
- **Records:** the counts add up, 503 tests, 342 reversals, 15 rows, 13 users and 102 client calls; the ten protected sections are byte-identical to `b04306d` in content, the last gaining only a blank separator line before the new section; the README's rules match the code for the 404 rule, the disclosure rule, the shape comparison, the deny-list words and the product-finding rule.
- **Scope:** 38 files under `proofs/stream-chat/`, the workflow, the architecture document and the evidence record; no dependency file, lock, `.npmrc`, `pyproject.toml` dependency or committed chat baseline changed; all 41 files mode 100644; no symlink under `proofs/` or `.github/`.

##### Checks and limits

| Check | Result |
|---|---|
| `git diff --check HEAD^1 HEAD` | no output, exit 0 |
| Installs, `env -i`, proxy and CA variables by reference | `pip install --require-hashes`: getstream 6.1.0, ruff 0.16.8, mypy 2.3.1, httpx 0.28.1; `pip check`: "No broken requirements found."; `npm ci --ignore-scripts`: "added 51 packages", "found 0 vulnerabilities"; stream-chat 9.53.0, ws 8.21.3, https-proxy-agent 5.0.1; `npm audit`: "found 0 vulnerabilities" |
| Unit tests, `env -i` | `Ran 503 tests in 37.730s`, `OK` |
| Ruff check / format / mypy | "All checks passed!" / "55 files already formatted" / "Success: no issues found in 53 source files" |
| `node --check` on the four `.cjs` files | exit 0 each |
| `checks/run_plan.py`, empty ledger | "run plan: fits", exit 0; run 1: 7 users, 4 channels, peak 4, 8 cases; V1 and V2: 2 users, 0 channels, peak 2, 18 cases each; total with reserve 18 of 20 users, 8 of 30 channels; complete set 132 cases |
| Pin test, `services/api` | `Ran 3 tests`, `OK` |
| `checks/fix_reversals.py`, scratch copy outside the tree | "reversals: 342, not demonstrated: 0", exit 0, about 12:29 to 13:07:21 UTC; 396 failed on an assertion, 47 on the error their reverted fix causes, 3 aborted by design; no syntax, import or name error; all 100 I2b rows OK, each failing on its rule's assertion or its reverted fix's error, every reason read |
| Secret scan of the diff, 707,890 bytes, and of the baseline | one JWT-shaped string, the fabricated redaction-test input, twice in the diff; 0 email addresses, private-key blocks, AWS, GitHub or Slack tokens, secret assignments; the application's API key 0 times in both |
| Baseline file | keys `app_id`, `video`, `feeds` only; no user, member, email or token; 130,016 bytes |
| Hosted CI | as above: PR run 36305061337 and push run 36298830899, seven jobs each, all success |
| Offline probes of my own | the `call` op bypass, finding 1; key casing, finding 3 |
| Repository | `git status` clean; only ignored paths created; the reversal scratch directory removed; no commit, push, PR comment, re-run, workflow dispatch or Notion change |

**Limits.** Nothing was run live, and the live results rest on I2b's record, whose outputs stayed in its session. I used no sub-agents. My probes were two, not a mutation campaign. The `sync` pair's two answers cannot be read from the record, nit 10. Whether the nine `PUT`s left every non-client role and setting unchanged is not shown by the record or the harness, finding 2, and only a live read can show it. Hosted CI was read for the head's PR run and the code head's push run, not for every push on I2b's branch.

#### Manager verification of the review (App Manager 5, 27 September 2026)

The session committed nothing, so there is no branch to check. The manager checked the report's claims against the reviewed head and made no Stream call.

- **Identity and classification.** The prompt revision, the head, its second parent, the merge base, the ancestor check and the diff's size are what the prompt expects. The manager's own runs used the same trusted policy (sha256 `dec69a26…`), outside the tree, with `python3 -I` and full SHAs. They gave the report's three results:
  - `main` → head: full scope, `behavior-or-empty`, **141 paths**. The report's "129 paths" is the count for `main` → `6a51dae`, the I2a review's, recorded above. The result itself is the same;
  - `6a51dae` → head: full scope, 55 paths; no non-Markdown path lies outside `proofs/stream-chat/` and the workflow;
  - head → `edbe592`: `ordinary-docs-only`, 11 paths.

  No non-Markdown path differs between `ad89753` and the head. I2b's 41 files are 38 under `proofs/stream-chat/`, the workflow, the architecture document and this record, all with mode 100644.
- **Findings, at `55b2238`:**
  - **Finding 1:** the `call` op (`client/runner.cjs:266`) applies any method of the SDK client to the command's arguments, and the client's `get`, `post`, `put` and `patch` take a full URL. The request interceptor (`:130`) checks only the budget, so only the `product` op (`:286`) applies `productRefusal`. `client_bridge.send` (`client_bridge.py:260`) passes any op and fields, and `validate` (`matrix.py:2035`) checks only `product` steps (`:2053`). The manager did not re-run the reviewer's probe; the code gives its result.
  - **Finding 2:** `products.verify` (`products.py:351`) flags an unverified read and a client role's non-empty grants, and nothing else. `configuration.product_differences` (`configuration.py:322`) is only that. The scoped `configure --apply` (`cli.py:258` to `:287`) compares its re-read with it and records only the client roles' grants (`_client_grants`, `:290`).
  - **Nit 3:** `denied_field` (`products.py:113`) and `deniedField` (`client/product-op.cjs:47`) compare keys exactly, and a denied-true key's value only with `true` or `"true"`. The path check lowercases (`:71`); the field check does not.
  - **Nit 4:** `_disclosure` (`proof_run.py:1773`) scans only the terms the request did not carry (`:1785`). With none left, nothing is found, and `no_leak_verdict` (`matrix.py:298`) gives HOLDS (filtered) on a 2xx whose control found the terms.
  - **Nit 8:** `_apply` (`cli.py:65`) raises on the first non-2xx, before the re-read and the record. The general `configure --apply` (`:191`) has the same shape. **One addition to the review's fix:** a charge or limit signal is raised inside `ServerApi.raw` (`server_api.py:188`), and the ledger does not refuse later requests. A re-read in a `finally` would therefore send requests after the signal. After a signal, the record must be written without any request.
  - **Nits 5, 6, 9 and 10,** in the record:
    - I2b's "Checks" item 4 reads "55 source files"; its step 2 line and App Manager 4's run read 53;
    - the live table has 15 rows. Section 5 of the I2b prompt names thirteen commands, the reserve rerun included. The two beyond them are command 3, a scoped dry run before run 1 besides the one before the apply, and command 8, `record-products-baseline`, which made no network call. No count gives eleven;
    - `93390ce` also changed FD-feed's custom note from `{fd_text}` to `feed of {A}` (`matrix.py`), and the deviation bullet names only the removed undo;
    - EO-channel's row in this record says "a list of two entries against one", and that the run's row keeps both normalized answers. The run's row is in I2b's local results file, which no record kept.
  - **Nit 7:** ADR 0003's consequences say "random and opaque" of Stream user IDs only. The architecture document's section 3 attributes the same rule for channel and message IDs to ADR 0003. Its section 8 states the rule without the attribution.
- **The manager's own record.** App Manager 4's verification of I2b repeated "the plan's eleven" in its disposition. It also did not flag item 4's 55, although its own mypy run printed 53. This is AM4-06; the disposition bullet is corrected in place.
- **Hosted CI.** The manager read both runs the report cites. PR run [36305061337](https://github.com/amthorn78/glow-dating-app/actions/runs/36305061337) on `84b2d6f` and push run [36298830899](https://github.com/amthorn78/glow-dating-app/actions/runs/36298830899) on `ad89753` each ran seven jobs, all success; "Stream proof checks" ran every step, each a success. The manager's commits since `55b2238` are Markdown only (`ordinary-docs-only` against the head), and PR27's run on `70a55c9`, [36320114309](https://github.com/amthorn78/glow-dating-app/actions/runs/36320114309), passed all seven jobs.
- **Not re-run by the manager:** the session's installs, tests, reversal run and two probes. Its tests, lint, mypy and reversal summary match I2b's record and App Manager 4's own run on `0a0512c`.

#### Disposition

- **I2b's code head `ad89753`, merged at `55b2238`, is approved.** No finding is blocking, and no recorded result changes.
- **The two design decisions that rest on I2b's live results are confirmed** (DM-01 P4):
  - removal and deactivation meet the history policy under the 404 code 16 rule;
  - what a user token can and cannot do in Video and Feeds before and after the lockdown, as the architecture document's sections 2, 3 and 6 record it.

  The manager marks I2b's claims in the architecture document's "Review" columns as confirmed, in this batch. The activities query stays open for the Dev Manager's close-out consultation, as App Manager 4's verification decided. DM-07 left it open and recorded, for P06.2; see "The Dev Manager's close-out read" at the end of this record.
- **Finding 1 is in the review prompt's class,** narrowly: a harness request could escape the deny-lists. So an offline correction pass, **P06.1-C4**, fixes it before P06.1 closes. Required:
  - no request to the Video or the Feeds host, or to a path under `/api/v2/video` or `/api/v2/feeds` once case, percent-encoding and dot segments are normalized, leaves the runner unless the product op's check allows it, whatever op sent it; a product path sent in a non-normalized form is refused outright. The check runs in the request interceptor, before the request is counted;
  - a `validate` rule that refuses a matrix step that reaches a product path through any op but `product`;
  - a test that drives the real runner through the review's scenario and fails without the fix (the error kind is `refused`, not `budget`); a check that the 18 product cases' steps still pass; and a reversal.
- **C4 also takes the other items, because it runs anyway.** Each code fix gets a test that fails without it, and a reversal.
  - **Finding 2:** `products.verify` also compares every non-client role's grants, each call type's settings and notification settings, and each feed group's recorded fields with the committed products baseline, as the chat check does with its own baseline. The scoped `configure`'s record keeps the full after-state. The README sentence and the architecture document's section 5 say what the re-read verified and what rests on Stream's documentation.
  - **Nit 3:** both tables match a denied key, and a denied-true key's value, in any letter case.
  - **Nit 4:** a no-leak case that succeeds when its own request carried every leak term is INCONCLUSIVE, not HOLDS (filtered); a refusal keeps its own rule.
  - **Nit 8:** a failed `PUT` mid-plan still leaves the record. It re-reads only when no charge or limit signal was met; after a signal it writes the record without any request.
  - **Nit 7:** the architecture document's section 3 states random, opaque channel and message IDs as its own design constraint, open for P06.2.
  - **Nits 5, 6, 9 and 10:** corrected in place in I2b's section, each marked. The two normalized `sync` shapes cannot be recovered. The record says so, and the architecture document says that "`sync` is an oracle too" rests on that one recorded observation.
- **Not in C4:** `checks/run_plan.py`'s mid-session reading, a recorded limit; no live run remains in P06.1.
- **Finding 2's live read** (the review: "the manager's call"): none now.
  - No verdict rests on it, and every lockdown body named only client roles (`is_lockdown_body`).
  - A read is a live command, and the Dev Manager reads its prompt first.
  - The question goes to the Dev Manager's close-out consultation; a read would run C4's corrected comparison. Until then, the records say that the other roles and the settings are unchanged on Stream's documentation, not by a re-read. DM-07 chose no read in P06.1: P06.2's first live step runs the comparison; see "The Dev Manager's close-out read" at the end of this record.
- **C4's exact-head review is P06.1's final delta review** (the brief's review plan). It covers C4's change and the manager's records since `55b2238`.
- **Manager-owned, in this batch:** ADR 0003's conditions and "Revisit when" (DM-05 finding 5 (b)); App Manager 4's disposition bullet above, corrected in place (AM4-06).

## P06.1-C4 corrections

Nathan ran this session from revision 1 of the [C4 correction prompt](../../ephemeral/2026-09-27-p06-1-c4-correction-prompt.md), from commit `2c2d450883937191c55905bd49fe7b0af0a186e8` (App Manager 5's manager branch `claude/magical-wozniak-yfmmx2`), on the session branch `claude/festive-ritchie-31vt3v`. It made no Stream call and no call to any other provider, and ran none of the harness's live commands. Commits: `634dc56` (the fixes), `a2ca27f` (the record corrections), `919a383` and `112011f` (what C4's own review found), `ff0f0b7` (this section, in draft, and two README limit sentences), `b2b9a0b` (a test that keeps an I2b reversal demonstrable; see "Checks" item 5), and the records commit that completes this section, the branch head named in the session's report. The code head is `b2b9a0b`; its source files are those of `112011f`.

### Environment and start gate

- None of `DATABASE_URL`, `HD_API_KEY`, `GEO_API_KEY`, `STREAM_APP_ID`, `STREAM_API_KEY` or `STREAM_API_SECRET` was present (names checked only). node v24.19.0, npm 11.9.0, npx 11.9.0 and Python 3.12.14, all from `/root/.local/bin`.
- The start gate passed: `git merge --ff-only 2c2d450…` onto the session branch; `git rev-parse HEAD` printed `2c2d450883937191c55905bd49fe7b0af0a186e8`; `git diff --stat 55b2238 HEAD -- proofs/stream-chat/ .github/` printed nothing.
- Installs and offline checks ran in clean processes (`env -i` with the path, home and locale; the proxy and CA variables passed by reference for the installs): `python3.12 -m venv .venv`, `pip install --require-hashes -r requirements-dev.lock`, `pip check` ("No broken requirements found."), `npm ci --ignore-scripts` ("found 0 vulnerabilities"). No dependency file changed.

### The review's items

Paths are under `proofs/stream-chat/`; line numbers are at `b2b9a0b` (the source as at `112011f`). Each fix has an offline test that fails without it and a reversal in `checks/fix_reversals.py` (the "C4 …" entries).

- **Finding 1, fixed.** Nothing reaches Video or Feeds except through the product op's check.
  - `client/runner.cjs:192` (`productRequestRefusal`), called first in the request interceptor (`:250`), before the budget, so a refused request is neither counted, sent nor recorded, error kind `refused`. It applies `productRefusal` to the method, the path as sent, the body and the query whenever the host is the Video or Feeds host or the path is a product path.
  - The URL is resolved as axios sends it (`sentURL`, `:142`: its `buildFullPath` against `config.baseURL`, then `new URL`).
  - Product paths are those under `/api/v2/video`, `/api/v2/feeds`, `/video` or `/feeds` once letter case, percent-encoding, backslashes and dot and empty segments are normalized (`client/product-op.cjs:84` to `:118`, `decodeOnce`, `normalizedPath`, `isProductPath`, shared by the runner). A product path not in its normalized form is refused outright; so is a path whose encoding does not settle in eight rounds, and a product body the check cannot read (`readableBody`, `:163`).
  - **A deliberate difference from the prompt's wording:** letter case is folded to find a product path but kept in the comparison with the normalized form. An ID may hold capitals (a Stream activity ID), and the allowlist's fixed segments are lower case, so a miscased fixed segment is still refused, by the op's check. C4's own review assessed this and found it sound (Go's router is case-sensitive, and a miscased ID gives nothing a lower-case one could not).
  - `glow_stream_proof/matrix.py:2060` (`_product_reach`, called by `validate`) refuses a `call` of one of the client's URL-taking methods (`CLIENT_URL_METHODS`, `:2055`: `get`, `post`, `put`, `patch`, `delete`, `sendFile`, `doAxiosRequest`, `setBaseURL`) and a `get` of a product path (`products.is_product_path`, `glow_stream_proof/products.py:199`). No case in the matrix did either (`validate(all_cases())` is `[]`).
  - Tests: `tests/test_runner.py` `ProductReachTest`:
    - the review's scenario (a REST user set, then a `call` of the client's `post` to the chat host's `/api/v2/video/call/default/x/join` with `ring: true`, zero budget, unreachable proxy): kind `refused`, "PROOF_REFUSED: denied path (join)", not `budget`;
    - non-normalized product paths; product hosts; the `get` op; bodies the check cannot read;
    - the 18 product cases' steps, with a run's placeholder values and with an activity ID in capitals: every one passes the new check and is stopped only by the zero budget.
  - `tests/test_matrix.py` `ProductReachValidationTest`.
- **Finding 2, fixed.** `products.verify` (`glow_stream_proof/products.py:428`) now also calls `baseline_differences` (`:488`). For each available product, that compares the following with the committed `baseline/video-feeds-1729640-2026-09-27.json` (`PRODUCTS_BASELINE`, `:83`):
  - every role's grants other than the client roles' (as sets);
  - each call type's `settings` and `notification_settings` (field by field, value and type, lists item by item, `_changed_paths`, `:458`);
  - each feed group's `default_visibility` and `default_follower_role`.

  A call type, feed visibility, feed group or role present on one side only is a difference. The client roles must still read `[]` (absent counts as `[]`).
  - What `baseline_record` keeps and is not compared, and why: `availability` has `verify`'s own rule; the read answers `read` and `feed_groups_read` describe the read, not the configuration. No kept field is a timestamp or otherwise volatile.
  - The scoped `configure --apply` record (`glow_stream_proof/cli.py:418`) keeps the full before- and after-state in `baseline_record`'s shape, scanned like every record.
  - `tests/fake_products.py` now models the committed baseline: every call type, visibility and feed group, every role's grants and every call type's settings. Preflight, the end of a run and the dry-run `configure` verify offline with no difference. `grant_before_lockdown()` puts the baseline's client grants back, and the plan is then the nine `PUT`s of the live apply; the tests' expectations moved from the old model to those nine `PUT`s.
  - Tests: `tests/test_products.py` `BaselineComparisonTest`: a changed `call_member` grant, a changed call-type setting, a changed notification setting and a type change, a type change inside a list, a changed feed group, roles and scopes on one side only, the client roles, an unavailable product, and the committed baseline itself (only its 18 client-role grants differ). Also `tests/test_cli.py` `ScopedConfigureTest` (the full after-state) and `ProbeAndBaselineTest` (a record written from the fake's read equals the committed baseline).
  - Records corrected: see below.
- **Nit 3, fixed.** `client/product-op.cjs:48` and `:65`, `glow_stream_proof/products.py:128` and `:147`: a denied key matches in any letter case, and a denied-true key's value matches `true` as a boolean or as `"true"` in any letter case, with the reason naming the field in lower case. Tests: `tests/test_products.py` `AllowlistTest`: eleven new table rows, driven through both tables with node, and `test_letter_case_does_not_matter_and_the_reason_names_the_field` (the same reason from the JS op, the Python op mirror and the guard's `denied`). The "I2b check 6" reversal was moved to the new helper and still fails for its reason.
- **Nit 4, fixed.** `glow_stream_proof/proof_run.py:1801` and `glow_stream_proof/matrix.py:305`: when the request carried every leak term, the row's `disclosure` detail says `nothing_scanned: true`, and a success is INCONCLUSIVE ("succeeded, but its own request carried every leak term, so nothing was left to scan"), never HOLDS (filtered). A refusal keeps its own rule. The new rule is in the README. Tests:
  - `tests/test_answers.py` `DisclosureRuleTest`: F9-sync with a request carrying every term, answered 201 (INCONCLUSIVE) and 403 (HOLDS);
  - `test_no_current_case_carries_every_leak_term_in_its_own_request`, which shows from the case definitions that every no-leak case with a step leaves terms to scan: R3, R4 and R5 three of four; R7a and R7b one of two; R8a two of four; R8b all three; F9-sync four of five; the four product no-leak cases all. That is the review's reading, so no recorded verdict changes;
  - `tests/test_matrix.py` `test_no_leak_verdict_with_nothing_scanned`.
- **Nit 5, corrected in the record** ("Checks" item 4 of "P06.1-I2b": mypy's 53 source files).
- **Nit 6, corrected in the record.**
  - The count is checked against section 5 of the I2b prompt, which names thirteen commands: `verify-clean` and the dry-run `configure` before any run, run 1, the probe, run V1, the baseline read, the scoped dry run and the apply, run V2, the one reserve rerun, and `verify-clean` with both dry runs after the last command.
  - The table's 15 add command 3 and command 8.
- **Nit 7, corrected in the architecture document**, section 3.
- **Nit 8, fixed, with the manager's addition.** `glow_stream_proof/cli.py:71` (`_apply`), `:121` (`_Applied`), `:164` (`_apply_recorded`), `:174` (`_read_after`), used by both `cmd_configure`'s general apply and `_configure_products`.
  - When a configuration write fails mid-plan, the command still writes its record: the steps applied so far (the step that raised with `status: null` and what stopped it), the failure, and the after-state.
  - The re-read runs only when no charge or limit signal was met, decided from `ledger.signals`, not from the exception's type, and when no Ctrl-C ended the apply. After a signal the record says "after-state not read: a charge or limit signal was met" and nothing more is sent.
  - A Stream refusal of a step exits 1. A signal's stop, the guard's refusal and a Ctrl-C reach `main` after the record (exit 3 for a signal).
  - A signal or Ctrl-C met by the re-read itself, even after a refused step, is recorded (`reread_failure`) and reaches `main`.
  - Tests: `tests/test_cli.py` `ConfigureRecordTest`, 12 tests:
    - a mid-plan 400 (the record holds the re-read), in both commands;
    - a mid-plan 402 and a mid-plan 429 in both commands (the fake counts no request after the signal, and the record is written);
    - a signal whose stop a Ctrl-C replaced (read from the ledger);
    - a Ctrl-C without a signal;
    - a signal in the re-read, alone and after a refused step;
    - a Ctrl-C in the re-read, alone and after a refused step.
- **Nit 9, corrected in the record** (the deviation bullet on `93390ce`).
- **Nit 10, corrected in the record and the architecture document.** No record holds the `sync` pair's two normalized answers; they are not reconstructed.
- **Optional: done.** The README says that the existence-oracle cases, not the disclosure rule, hold the question of whether an echoed identifier signals existence.

### C4's own review

A fresh reader, a read-only sub-agent of this session, reviewed the code diff at `634dc56` under the prompt's rules: no network, no environment value, no change, and no run of `fix_reversals.py`. It then re-checked `919a383` and `112011f`.

**Blocking at `634dc56`: one undecodable percent-escape switched the new check off, in both languages.**
- `decodeURIComponent` in the runner, and Python's strict `unquote` in `validate`, threw on a valid-hex escape that is not UTF-8 (`%ff`, `%c0`). The decoding loop then stopped with nothing decoded.
- So `POST …/api/v2/%76ideo/call/default/abc%ff/join` with `ring: true` was not seen as a Video path and reached only the budget. The reviewer showed offline, with Go 1.24's `http.ServeMux`, that such a path routes to the join handler.
- **Fixed at `919a383`:** decoding is byte by byte in both languages and never throws; a path that does not settle is refused. A table test (`tests/test_products.py` `ProductPathTest`) runs the runner's `normalizedPath` and the Python `normalized_path` on the same 17 paths.

This was a false-pass path in finding 1's own fix, so it was fixed here, with tests and reversals, before any report.

**Further items from the review, fixed at `919a383`:**
- the runner sends to no host but Stream's chat, Video and Feeds hosts, and refuses a `Host` header;
- no redirect is followed (`maxRedirects: 0` on every request);
- the bare `/video` and `/feeds` forms are product paths;
- JSON inside a query value is read by the deny-list;
- the baseline comparison walks lists item by item;
- the step that met a signal stays in the record;
- a Ctrl-C during the re-read still writes the record.

**The re-check of `919a383` found one should-fix, fixed at `112011f`:** after a refused step, a signal or Ctrl-C met by the re-read was recorded but not re-raised. With it, `112011f` also sends `https:` only and refuses forwarding headers (`X-Forwarded-Host`, `Forwarded`, `X-Original-Host`, `X-Host`).

**The re-check of `112011f`: nothing blocking and no should-fix.** Its two nits are recorded as README limits:
- two request-rewriting headers (`X-HTTP-Method-Override`, `X-Original-URL`) still pass the check. They matter only if Stream honours them (corrected in P06.1-C5; the C4 review's finding 1: this said that only a `call` of a client URL method, which `validate` refuses, could set them, but other stream-chat methods take a request-options argument too). Since P06.1-C5, `validate` covers the matrix's steps: every `call` step must be on its allowlist, with no more positional arguments than listed, so no step reaches a request option. The runner refuses those two headers and `X-HTTP-Method`, `X-Method-Override` and `X-Rewrite-URL`, in any letter case and with an underscore for a hyphen, on every request, whatever sent it. What remains is a per-request `proxy`, `socketPath` or adapter, none of which gets past the runner's host and path checks; the README's limits also list the other routing headers and JSON nested two levels deep (pointer added by App Manager 5 after the exact-head review of C5, its nit 1);
- another re-read failure after a refused step exits 1.

**Residuals the reviewer assessed and the README records:**
- a per-request `proxy` or `socketPath`, the fetch adapter, and two-level nested JSON in a query value: none reaches Video or Feeds past the check;
- the WebSocket's host: it follows the base URL, which only `setBaseURL`, refused by `validate`, changes. A refusal inside the WebSocket's constructor would make the SDK retry.

**Found by C4 in its own reading:** a product request whose body the check cannot read (a string that is not JSON, which axios sends form-encoded). Fixed at `634dc56` with a test and a reversal.

### Records corrected

- **`proofs/stream-chat/README.md`:**
  - finding 1: the runner's check on every request;
  - finding 2: what the verification compares, the record's full state, and the sentence "that Stream changes only the roles named is documented and verified by the re-read after the apply, not assumed". It now says the re-read of 27 September compared the client roles' grants only, that the other roles and the settings being unchanged rests on Stream's documentation, and that the corrected verification compares them at the next live use;
  - nit 3 and nit 4 (the new verdict rule);
  - nit 8;
  - the optional sentence;
  - "Limits", "Added in P06.1-C4".
- **`docs/architecture/chat-provider-permissions.md`:**
  - section 3's existence-oracle row: the constraint is the document's own (DM-05 finding 5 (a)), not ADR 0003's, open for P06.2 (nit 7); "`sync` is an oracle too" rests on the one recorded observation (nit 10);
  - section 5: the Stream-documentation sentence, "the re-read showed no difference from the target" and the "Untouched" paragraph (finding 2).

  Its status line and "Review" columns are unchanged.
- **This record, in I2b's own subsections**, each marked "(corrected in P06.1-C4; the I2b review's nit N)":
  - "Results by topic", EO-channel's row (nit 10);
  - "Checks" item 4 (nit 5);
  - "Deviations and limits": the `93390ce` bullet (nit 9) and the command count (nit 6);
  - "What P06.2 and the delta review must know" (nit 10).

  Every other part of the record is byte-identical to `2c2d450`, the manager's verification of I2b and the exact-head review of I2b included; this section is appended at the end.

### Checks

1. `git diff --check 2c2d450883937191c55905bd49fe7b0af0a186e8 HEAD`: no output, exit 0.
   - `git diff --name-only 2c2d450… HEAD`: 17 paths, all owned: `docs/architecture/chat-provider-permissions.md`, this record, and 15 under `proofs/stream-chat/`:
     - `README.md`, `checks/fix_reversals.py`;
     - `client/product-op.cjs`, `client/runner.cjs`;
     - `glow_stream_proof/cli.py`, `matrix.py`, `products.py`, `proof_run.py`;
     - `tests/fake_products.py`, `test_answers.py`, `test_cli.py`, `test_configuration.py`, `test_matrix.py`, `test_products.py`, `test_runner.py`.
   - No dependency file, lock, `.npmrc`, `pyproject.toml` or committed baseline changed; every file is mode 100644, and there is no symlink.
2. **Classification:** the trusted policy from `origin/main` (`0f45e64`, sha256 `dec69a26…`), extracted to a temporary directory outside the tree and run as `python3 -I …/change_scope.py --base 2c2d450883937191c55905bd49fe7b0af0a186e8 --head <head> --merge-base`, gave `{"full": true, "reason": "behavior-or-empty", …}` at `919a383`, and again at `8077eea`, the last commit before this sentence: full scope, as expected, 17 paths each time. This sentence's commit adds Markdown only.
3. **Installs:** as above.
4. **Offline checks** at `112011f` and again at `b2b9a0b`, the same results:
   - unit tests: `Ran 543 tests`, `OK` (503 at the start, `Ran 503 tests … OK`);
   - Ruff: "All checks passed!" and "55 files already formatted";
   - mypy: "Success: no issues found in 53 source files";
   - `node --check` OK for `error-info.cjs`, `product-op.cjs`, `request-log.cjs` and `runner.cjs`;
   - `checks/run_plan.py` with an empty ledger (no `.work` directory): "run plan: fits".
5. **Fix reversals** (`checks/fix_reversals.py`, from a scratch copy of the directory outside the tree):
   - at the start: "reversals: 342, not demonstrated: 0", exit 0, 15:35:39 to 16:05:29 UTC;
   - at `112011f`: "reversals: 378, not demonstrated: 1", exit 1, 16:38:41 to 17:12:20 UTC. The one was "I2b products: the runner asks the op before a product request is sent": with the product op's own check removed, `EveryOpTest` still passed, because C4's request check now refuses the same requests with the same reasons. The fix is test-only (`b2b9a0b`): `EveryOpTest` also sends a product path carrying a query, which only the op's own check refuses. With the op's check reverted, that command reaches the budget (`'budget' != 'refused'`);
   - **at `b2b9a0b`, the code head: "reversals: 378, not demonstrated: 0", exit 0, 17:14:54 to 17:47:45 UTC** (342 at the start, 36 C4 entries added). Every row OK. The failure reasons read 456 `AssertionError`s and 49 errors each naming the error its reverted fix causes, with 3 test processes stopped by design (Ctrl-C). None failed through a syntax, import or name error;
   - the C4 entries were also run as a subset, with the two "I2b check 6" entries whose pattern moved: 23 at `634dc56` and 35 at `919a383`, "not demonstrated: 0" each time; the full run at `112011f` covers all 36. Every one failed on its test's assertion or on the error its reverted fix causes, none through a syntax, import or name error, none by Ctrl-C. For example:
     - finding 1: `'budget' != 'refused'`;
     - finding 2: `Lists differ: [] != ["video call type default: grants for call_member differ …"]`;
     - nit 3: `[None, None, None, None] != ['denied field (ring)', …]`;
     - nit 4: `'HOLDS (filtered, not refused)' != 'INCONCLUSIVE'`;
     - nit 8: `16 != 11` (calls sent after the signal), and `glow_stream_proof.cli.StepRefused: PUT … failed; stopping` (the error the reverted fix lets escape, with no record written);
     - the review's items: `'/api/v2/%76ideo/call/default/abc%ff/join' != '/api/v2/video/call/default/abcÿ/join'` and `'budget' != 'refused'`.
6. **Secret scan** of the whole diff `2c2d450..HEAD` (about 197 KB): no JWT-shaped string, email address, private-key block, AWS, GitHub or Slack token, or secret assignment, and 0 occurrences of the application's API key.
7. **Foundation, on this branch:**
   - run 351 on `634dc56` was cancelled by the next push;
   - run 352 on `a2ca27f` succeeded (Markdown only against the previous push);
   - run 353 on `919a383` succeeded;
   - run 354 on `112011f` was cancelled by the next push; run 355 on `ff0f0b7` succeeded (Markdown only against the previous push);
   - **run 356 on the code head `b2b9a0b`** ([36336214481](https://github.com/amthorn78/glow-dating-app/actions/runs/36336214481)), 17:14:51 to 17:21:04 UTC, all seven jobs success: Change scope, API checks, API artifact checks, API mobile smoke, Mobile checks (the rendered suite included), "Stream proof checks" (ran, not skipped; every step success: the hash-locked install, `pip check`, `npm ci --ignore-scripts`, the tests under `env -i`, Ruff, format, mypy, `node --check` on every `.cjs` file, `checks/run_plan.py`) and the Foundation gate. The records commit that completes this section is Markdown only, pushed after run 356 finished so that it did not cancel it.

   Nothing was re-run or dispatched.

### Deviations and limits

- **Beyond the review's ten items, C4 fixed what its own review found**, each with a test and a reversal. That was one blocking gap in finding 1's first fix (the `%ff` escape), a should-fix in nit 8's first fix, and ten further items, all in the class the prompt allows: letting a change escape the deny-lists, or sending a request after a signal.
  - Two of those items widen nothing and narrow what the runner may send: only `https:` to Stream's three hosts, and no redirect.
  - `maxRedirects: 0` has no offline test: showing it needs a server that redirects, and the runner sends to no host but Stream's. It is the one change without a reversal.
- **Letter case is kept in the normalized-form comparison**, as described under finding 1, rather than making every product path with a capital "not normalized". The prompt's requirement is met: any miscased fixed segment is refused.
- **Nothing here is exercised live.** No live run remains in P06.1; the fixes are first used live in a later phase.
- **The fake products changed.** They now model the committed baseline instead of a guessed two-type model, so tests that asserted the old plan (four `PUT`s, two call types) now assert the live plan (nine `PUT`s, four call types, five visibilities, six feed groups). No verdict test changed; the capability knob `allowed` is unchanged.
- **Not in this pass:** `checks/run_plan.py`'s mid-session reading, as the prompt says.

### What the final delta review and P06.2 must know

- **Rules that changed.**
  - The runner refuses a request whatever op made it: any host but Stream's three; any protocol but `https:`; a `Host` or forwarding header. For a product host or path, the product op's check applies, and a product path or body it cannot read in normalized form is refused.
  - `validate` refuses a `call` of a client URL method and a `get` of a product path.
  - `products.verify` compares everything the committed products baseline records.
  - A no-leak success with nothing scanned is INCONCLUSIVE.
  - Both deny-list tables ignore letter case.
  - A configure apply always leaves a record and sends nothing after a signal.
- **Not yet exercised live:**
  - every C4 fix;
  - in particular the baseline comparison. At the next live use it may report a difference that is Stream's rather than the lockdown's, for example a setting added since 27 September. Such a difference stops preflight and must be reported, never assumed away;
  - `maxRedirects: 0` on every chat request.
- **For the delta review:** C4's change is `2c2d450..<head>`, with `634dc56`, `919a383` and `112011f` the code commits. The reviewer's probe scripts stayed in this session's scratch directory.

### Manager verification of C4 (App Manager 5, 27 September 2026)

App Manager 5 checked the relayed report against the pushed branch. The manager makes no call to Stream.

- **Identity:**
  - branch `claude/festive-ritchie-31vt3v`, head `c83bedf1f812cf454d4f16b5dc741c5d944749d9`, tree `52e33648ffb8d02429d434dc8e3de609579d92a2`, as reported. Ten commits on the start `2c2d450`, with one merge base. The code commits are `634dc56`, `919a383`, `112011f` and `b2b9a0b` (a test only); the other six change only Markdown. The code head is `b2b9a0b`;
  - 17 files, +2,381 and −204: 15 under `proofs/stream-chat/`, the architecture document and this record. Every path is owned. No dependency file, lock, `.npmrc`, `pyproject.toml`, committed baseline or workflow changed. Every file has mode 100644, there is no symlink, and `git diff --check` is clean;
  - this record: outside C4's appended section, five lines changed, all in I2b's own subsections, each a correction the prompt listed, marked. Every other line is byte-identical to `2c2d450`, the manager's verification of I2b and the exact-head review of I2b included;
  - the architecture document: only section 3's existence-oracle row (nits 7 and 10) and three passages of section 5 (finding 2) changed. Its status line and "Review" columns are as the manager set them.
- **Classification:** the trusted policy from `main` (`0f45e64`, sha256 `dec69a26…`), outside the tree, with `python3 -I` and full SHAs: `2c2d450` → `c83bedf` is full scope (`behavior-or-empty`), 17 paths.
- **Code read,** the whole diff of the production code, about 710 changed lines:
  - **finding 1:** the request interceptor calls `productRequestRefusal` before the budget, so a refused request is neither counted nor sent. It allows `https:` only, to Stream's three hosts only, and refuses a `Host` header and four forwarding headers. The path is normalized by `normalizedPath` (byte-wise decoding for up to eight rounds, dot and empty segments resolved); a product path not in its normalized form, a path that does not settle, and a product body that is not JSON are refused. `maxRedirects` is 0 on every request. `validate` refuses a `call` of one of `CLIENT_URL_METHODS` and a `get` of a product path;
  - **finding 2:** `baseline_differences` compares the non-client roles' grants as sets, the call types' `settings` and `notification_settings` through `_changed_paths` (value and type, lists item by item), and the feed groups' two recorded fields. A scope or a role on one side only is a difference. The scoped record keeps `baseline_record` of the before- and the after-state;
  - **nit 8:** `_apply` keeps each answered step, and the step that raised with what stopped it. `_read_after` re-reads only when `ctx.ledger.signals` is empty and no Ctrl-C ended the apply; `ctx.ledger` is the ledger `ServerApi` records its signals in (`cli.Context`). `finish()` re-raises a stop only after the record is written;
  - **nit 4:** INCONCLUSIVE only for a success with nothing scanned; a refusal keeps its rule. **Nit 3:** both tables lower-case the key and the value `"true"`;
  - the fake products now read the committed baseline for every scope, role and setting. The capability knob `allowed`, on which the verdict tests rely, is unchanged.
- **Offline re-run,** in a scratch export of `c83bedf`, in clean processes without any `STREAM_*` variable, the installs with the proxy and CA variables by reference:
  - `pip install --require-hashes -r requirements-dev.lock` and `pip check` ("No broken requirements found."); `npm ci --ignore-scripts` ("found 0 vulnerabilities");
  - unit tests: `Ran 543 tests`, `OK`. Ruff check: "All checks passed!"; Ruff format: "55 files already formatted"; mypy: "Success: no issues found in 53 source files". `node --check` on the four `.cjs` files: OK. `checks/run_plan.py` with an empty ledger: "run plan: fits";
  - `checks/fix_reversals.py`, from the export: "reversals: 378, not demonstrated: 0", exit 0, 18:55:36 to 19:24:01 UTC. Every row is OK: 456 failures on an assertion, 49 on the error the reverted fix causes, and 3 test processes stopped by Ctrl-C by design, none through a syntax, import or name error;
  - the manager read the reasons of all 36 C4 entries. Each fails on its test's assertion (for example `'budget' != 'refused'`, `16 != 11` for the calls sent after a signal, `'HOLDS (filtered, not refused)' != 'INCONCLUSIVE'`), or, for nit 8's record, on the `StepRefused` its reverted fix lets escape. The I2b entry that `b2b9a0b` keeps demonstrable fails on `'budget' != 'refused'`.
- **Secret scan** of the whole diff (229,207 bytes): 0 JWT-shaped strings, email addresses, private-key blocks, AWS, GitHub or Slack tokens and secret assignments.
- **Hosted CI on C4's branch:**
  - push run 356 ([36336214481](https://github.com/amthorn78/glow-dating-app/actions/runs/36336214481)) on the code head `b2b9a0b`: all seven jobs succeeded. "Stream proof checks" ran every step, not skipped, and Mobile checks ran the rendered suite;
  - run 353 on `919a383` succeeded. Runs 351 on `634dc56` and 354 on `112011f` were cancelled by the next push, as the report says;
  - runs 352, 355, 357 and 358 were on Markdown-only commits. Run 358 on the head skipped the application jobs by design, and its gate passed.
- **Two slips in C4's section, no effect:**
  - "Checks" item 6 gives the scanned diff as "about 197 KB"; the whole diff at the head is 229,207 bytes, as C4's report says;
  - "What the final delta review and P06.2 must know" lists `634dc56`, `919a383` and `112011f` as the code commits and leaves out `b2b9a0b`, which changes a test. The section's first paragraph names it.

#### Dispositions

- **C4 is verified and integrated** into the manager branch by fast-forward, at `c83bedf`. The ten items are fixed, each code fix with a test that fails without it and a reversal, as the prompt required. The record corrections are the ones the disposition listed.
- **The deviations are accepted:**
  - **beyond the ten items,** C4 fixed one blocking gap and one should-fix in its own first fixes, and ten further items its own review found. All are in the class the prompt allowed (a request that could escape the deny-lists, or a request after a signal). Each narrows what the harness may send, and none widens it;
  - **`maxRedirects: 0` without a test:** the one change without a test and a reversal. C4's exact-head review assesses whether an offline test is feasible;
  - **letter case kept in the normalized-form comparison,** a departure from the prompt's wording. The prompt's requirement holds: a miscased fixed segment is refused by the allowlist, and an activity ID may hold capitals. The review assesses it;
  - **the fake products model the committed baseline:** the tests of the plan now assert the live nine-`PUT` plan, and no verdict test changed. The review assesses whether any test is weaker;
  - **the README limits** (the WebSocket's host, a per-request `proxy` or `socketPath`, the fetch adapter, two-level nested JSON in a query value, and two request-rewriting headers). The review checks that each is unreachable, as recorded.
- **Not yet exercised live:** every C4 fix. The baseline comparison may report, at the next live use, a difference that is Stream's rather than the lockdown's. It stops preflight and must be reported, never assumed away.
- **C4's exact-head review is next.** It is P06.1's final delta review, offline, of `c83bedf`.

### Exact-head review of C4 (27 September 2026)

Nathan ran the review session from revision 1 of the [review prompt](../../ephemeral/2026-09-27-p06-1-c4-review-prompt.md) (records commit `f17b111`) and relayed its report to App Manager 5. The relay does not name the model and level he picked. The session committed and pushed nothing, and made no Stream call.

- **Verdict: changes required.** C4's change is sound apart from one should-fix finding, which the review places, narrowly, in the class that gets another offline correction pass: `matrix.validate` does not refuse every stream-chat method whose arguments reach a request's configuration or path, and the README's recorded limits rest on it doing so. No current step reaches such an argument, and the harness has made no live call since C4.
- **Four nits,** none in the class: `maxRedirects: 0` has no test, and one is feasible; ADR 0003's condition (c) still says a limit "stands until P06.1-C4"; a failed record write after a signal loses the stop's exit code; one test of nit 8's ledger rule shows less than its name says.
- **The rest is confirmed.** The I2b review's ten items and the items C4's own review found are fixed, apart from the `validate` half of finding 1. The review agrees with the manager's dispositions except the README limits, where it disagrees in part.

#### The report, as relayed

The session's notes before its report, as relayed (the relay begins mid-session), verbatim:

> Continuing with the rest of the review: the nit 8 and finding 2 tests, the fake products, the records and CI. I'm leaving further adversarial probing of the request check out of this review.
>
> Tests read. Now checking the records: the evidence record's in-place changes against `2c2d450`, and the architecture document.
>
> The reversal run is partway through (the C3 entries). Meanwhile I'm running the secret scan and reading the C4 reversal entries.
>
> Now checking hosted CI (read-only).
>
> CI is green on both runs. Next, the C4 reversal entries while the full run finishes.
>
> While the reversals finish, a quick differential check that the runner's `normalizedPath`/`isProductPath` and the Python mirror agree on random inputs (a pure equivalence test).
>
> Offline checks, CI, records and tests are read. I'm now waiting for two things: the full reversal run (about half done) and the read-only research agent on stream-chat's URL-taking methods.
>
> Both background jobs are still running: the full reversal run (177 of 378 entries done so far) and the read-only stream-chat inventory agent. I'll write the report once both are back. So far there is no blocking finding.
>
> The research agent is back. I'll use its result only at the level of which SDK methods pass caller options into the request configuration, and I'll check that against the matrix's steps. Two quick checks: the method signatures, and whether any current step passes such an argument.
>
> No current matrix step exposes this issue since none pass request-options or call the path-building methods—the real gap is in validate's coverage and the README's documented limits. Now checking the reversal run.
>
> The reversal run has about 106 of 378 entries left, roughly ten minutes. I'll read every C4 entry's failure reason when it finishes, then write the report.
>
> Writing the report. First, the path counts of the three classification outputs.

The report, verbatim (its headings one level down):

**Verdict: changes required.** C4 is sound apart from one should-fix finding, which I place (narrowly) in the class that gets another offline correction pass. `matrix.validate` does not refuse every SDK method whose arguments reach the request's configuration or path, and the README's recorded limits rest on it doing so. Everything else is nits or records.

- **Prompt:** revision 1, from `f17b11146f37b8ee93b92ddefb52fde2cc19ac01`.
- **Head reviewed:** `git rev-parse HEAD` printed `c83bedf1f812cf454d4f16b5dc741c5d944749d9`. The merge base is `0f45e64`, the head is an ancestor of `f17b111`, and the diff is 17 files, +2381 −204.
- **Classification:** trusted policy from `main` (sha256 `dec69a26…`), run outside the tree with `python3 -I` and full SHAs:
  - `main` → head: `{"full": true, "reason": "behavior-or-empty"}`, 145 paths;
  - `55b2238` → head: `{"full": true, "reason": "behavior-or-empty"}`, 31 paths. The non-Markdown filter outside `proofs/stream-chat/` printed nothing;
  - head → `f17b111`: `{"full": false, "reason": "ordinary-docs-only"}`, 7 paths.
- **Environment:** none of the six variables is present. On the default PATH, `node` is `/opt/node22/bin/node` v22.22.2 and npm is 10.9.7. The pinned toolchain in `$HOME/.local/bin` is node v24.19.0, npm 11.9.0 and Python 3.12.14; I put it first on PATH for every check.

##### Findings, most severe first

**1. Should fix. `validate` misses methods that can steer a request, and the README's limits depend on it.** In class: yes, narrowly.
- **Where:** `glow_stream_proof/matrix.py:2055` (`CLIENT_URL_METHODS`) and `:2060` (`_product_reach`); `README.md:398`.
- **The gap:** stream-chat 9.53.0 has more methods whose JSON arguments reach the request than the eight `validate` refuses.
  - These client methods take a request-options argument that the SDK passes into the request configuration: `queryUsers`, `searchUserGroups`, `queryChannelsRequestWithResponse`, `search`, `searchRoles`, `uploadFile` and `uploadImage`.
  - So do three channel methods: `sendFile`, `sendImage` and `queryMembers`. `validate` does not check the channel target at all.
  - `createReminder`, `updateReminder` and `deleteReminder` put a caller value into the request path without encoding it.
- **Scenario:** the README says the residual request options (a per-request `proxy` or `socketPath`, the fetch adapter, and the two request-rewriting headers) are reachable "only [through] a `call` of a client URL method", which `validate` refuses. They are reachable through the methods above, and `validate` passes such a step.
- **What holds:**
  - The runner's check still runs on every HTTP request and resolves the final URL, so the host and product-path checks still apply.
  - No current matrix step passes a request-options argument or calls a reminder method. I checked every `call` step in `all_cases()`.
  - No live run remains in P06.1, so exposure today is nil.
  - The escape is the one C4 already recorded: a rewrite header that Stream might honour.
- **Fix:**
  - Make `validate` an allowlist of the (target, method, maximum positional arguments) the matrix uses, or refuse any request-options argument and the reminder methods on either target.
  - Add a test and a reversal.
  - Correct `README.md:398`.
- **Why the class:** the same reasoning as the I2b review's finding 1. A harness-authored step could reach what the recorded mitigation says it cannot.

**2. Nit: `maxRedirects: 0` has no test, and an offline one is feasible.** Not in class.
- **Where:** `client/runner.cjs:250`.
- **What it changes:** axios 1.20.0 then uses the native `https` transport, not follow-redirects, and its fetch adapter sets `redirect: 'manual'`. A 3xx comes back as Stream's non-2xx answer, which is never a pass. No chat case relies on a redirect, and no live run recorded one.
- **Fix:** load `runner.cjs` with a stub `stream-chat` in `require.cache` (the technique the runner already uses for `isomorphic-ws`). Capture the registered request interceptor, call it with a chat config, and assert `maxRedirects === 0`. Add a reversal.

**3. Nit, records: ADR 0003's condition (c) says the re-read limit "stands until P06.1-C4".** Not in class.
- **Where:** `docs/adr/0003-chat-display-rule.md`, "Conditions" (c); manager-owned.
- C4 changed the harness's comparison, not what was read live. That the other roles and the settings are unchanged still rests on Stream's documentation until a live read, which the manager deferred to the Dev Manager's close-out.
- **Fix:** say so, and point section 4 (c) of the architecture document at section 5's corrected wording.

**4. Nit: a failed record write after a signal loses the stop's exit code.** Not in class.
- **Where:** `glow_stream_proof/cli.py:335` and `:421`, where `write_json` runs before `outcome.finish()`.
- **Scenario:** after a signal, if the write itself raises (the leak check refuses the record, or the disk write fails), that error replaces the signal's stop. The command then exits 1 with a traceback instead of 3, and no line names the signal. Nothing is sent either way.
- **Fix:** run `finish()` in a `finally` around the write, or chain the write's error to the stop.

**5. Nit, test strength.** Not in class.
- **Where:** `tests/test_cli.py`, `test_the_signal_is_read_from_the_ledger_not_the_exception`.
- The test replaces the stop with a Ctrl-C, which on its own already blocks the re-read. So it shows the record's label, not that the ledger rule prevents a request.
- A variant where an ordinary error replaces the stop would show that. The code itself is correct.

##### The I2b review's items and C4's own review

| Item | Status |
|---|---|
| Finding 1 | Fixed in the runner: the check runs first in the interceptor, before the budget, whatever op sends the request. The `validate` half is incomplete (finding 1 above) |
| Finding 2 | Fixed: non-client roles as sorted lists, settings field by field with type and list items, feed groups' two fields; full before- and after-state in the record |
| Nit 3 | Fixed: both tables fold key and value case and give the same reasons (node-driven test, four reversals) |
| Nit 4 | Fixed: INCONCLUSIVE only for a success with nothing scanned. The other no-leak call sites do not use the disclosure rule, so they are unaffected; no current case carries every term |
| Nit 8, with the manager's addition | Fixed: no request after a 402 or 429 on a step or on the re-read; the signal is read from `ctx.ledger.signals` (the same ledger `ServerApi` records in); the record is always written; exit 3, 1 or Ctrl-C as recorded. Nits 4 and 5 above apply |
| Nits 5, 6, 7, 9, 10 | Corrected. Nit 6's count checked: the I2b prompt's section 5 names 13 commands |
| C4 review: `%ff` (blocking) | Fixed: byte-wise decoding. JS and Python agree on 20,000 random paths |
| C4 review: should-fix and the ten further items | Fixed, each with a test and a reversal, except `maxRedirects` (nit 2 above) |
| C4 re-check nits (the two rewrite headers) | Recorded as limits, but the reachability claim is wrong (finding 1 above) |

##### The manager's dispositions

- **C4 verified and integrated:** agree, subject to finding 1.
- **Fixes beyond the ten items:** agree. Each narrows what may be sent.
- **`maxRedirects` without a test:** agree it is not blocking. A test is feasible (nit 2).
- **Letter case kept in the normalized-form comparison:** agree. It is sound: the deny-list folds case, the allowlist's fixed segments are case-sensitive, so a miscased fixed segment is refused, and an ID keeps its case.
- **Fake products model the committed baseline:** agree. No verdict test is weaker: the fake's behaviour depends only on group existence and the `allowed` knob, not on grants. The plan tests now assert the live nine `PUT`s.
- **README limits:** disagree in part. The WebSocket-host claim holds: only `setBaseURL` changes `wsBaseURL`. The fetch-adapter claim holds. "Only a client URL method could set them" does not hold (finding 1).
- **Not yet exercised live:** agree.
- **The two slips:** agree. The diff is 229,207 bytes, and `b2b9a0b` is missing from the code-commit list.

##### Areas with no findings

- Nit 4 creates no new HOLDS path.
- A `refused` reply records no request, so it reads INCONCLUSIVE, never HOLDS.
- The new check refuses nothing a chat case sends. Chat paths are not product paths, chat requests carry no host or forwarding header, and uploads go to chat paths.
- Baseline differences carry the `video/feeds:` prefix, so they do not block the chat-only gate on the scoped apply.
- The SDK registers no interceptor of its own. Its insights path, which bypasses the client's axios instance, is off in the runner and no method turns it on.
- The fix reversals remove their fixes and fail for the right reasons (under Checks).
- The records match the code, and every `file:line` I checked is right.
- The evidence record is byte-identical to `2c2d450` apart from the five marked single-line corrections and the appended section.
- Scope: 17 paths, all mode 100644, no symlink, and no dependency, lock, baseline or workflow file.

##### Checks

| Check | Result |
|---|---|
| `git diff --check 2c2d450… HEAD` | no output, exit 0 |
| Installs (clean env, proxy/CA by reference) | pip `--require-hashes` OK; `pip check` "No broken requirements found."; `npm ci --ignore-scripts` "found 0 vulnerabilities"; stream-chat 9.53.0, axios 1.20.0 |
| Unit tests | `Ran 543 tests`, `OK` |
| Ruff / format / mypy | "All checks passed!" / "55 files already formatted" / "Success: no issues found in 53 source files" |
| `node --check` on the four `.cjs` files | OK |
| `checks/run_plan.py`, no `.work` | "run plan: fits", exit 0 |
| `checks/fix_reversals.py`, scratch export | "reversals: 378, not demonstrated: 0", exit 0, 20:46:46 to 21:13:57 UTC. 456 assertion failures, 49 errors, 3 by-design Ctrl-C stops, no syntax, import or name error. All 36 C4 rows OK, each failing on its rule (for example `'budget' != 'refused'`, `16 != 11`, `'HOLDS (filtered, not refused)' != 'INCONCLUSIVE'`, `StepRefused` escaping). The I2b row kept by `b2b9a0b` fails on `'budget' != 'refused'` |
| JS/Python normalization, differential | 20,000 random paths, 0 disagreements |
| Secret scan of the diff (229,207 bytes) | 0 JWT-shaped strings, emails, private keys, AWS, GitHub or Slack tokens, or secret assignments |
| CI push run 356 ([36336214481](https://github.com/amthorn78/glow-dating-app/actions/runs/36336214481)) on `b2b9a0b` | 7 jobs success; "Stream proof checks" ran every step, not skipped |
| CI PR27 run 366 ([36345354254](https://github.com/amthorn78/glow-dating-app/actions/runs/36345354254)) on `f17b111` | 7 jobs success; "Stream proof checks" ran every step, not skipped; gate passed |

##### Limits

- Nothing was run live.
- The API key's value was not available, so the scan could not search for it.
- The SDK method inventory came from one read-only sub-agent reading the installed package. I confirmed the method signatures and the matrix steps myself.
- Beyond reading the check and running the offline tests above, I did not probe the runner's request check adversarially.
- `maxRedirects` behaviour comes from the axios source; it was not exercised.

I changed nothing in the repository, on GitHub or in Notion; `git status` is clean at `c83bedf`.

**DECISION NEEDED:** whether finding 1 gets another offline correction pass before P06.1 closes. I recommend a small one: `validate` becomes an allowlist of the methods and argument counts the matrix uses, with a test and a reversal, and `README.md:398` is corrected. The nits can ride in the same pass or go into the records.

#### Manager verification of the review (App Manager 5, 27 September 2026)

The session committed nothing, so there is no branch to check. The manager checked the report's claims against the reviewed head `c83bedf`, in the scratch export it verified C4 in (identical to the head's harness) and in the stream-chat 9.53.0 and axios 1.20.0 that export installed. It made no Stream call.

- **Identity and classification.** The prompt revision, the head, the merge base, the ancestor check and the diff's size are what the prompt expects. The three classification results and path counts (145, 31 and 7) are the ones the manager's own runs gave before it gave the prompt, with the same trusted policy.
- **Finding 1, confirmed:**
  - `_product_reach` (`matrix.py:2060`) refuses only a `call` on the client target naming one of the eight `CLIENT_URL_METHODS` (`:2055`), and a `get` of a product path. It does not look at the channel target or at the number of arguments;
  - in stream-chat 9.53.0 (`dist/cjs/index.node.js`), `get(url, params, config)` hands its third argument to `doAxiosRequest` as `options.config`, and `_enrichAxiosOptions` spreads it into the axios request configuration (`...options.config`), after the SDK's own headers. The client's `queryUsers`, `searchUserGroups`, `queryChannelsRequestWithResponse`, `searchRoles` and `search` take such an argument (`requestOptions`), and the channel's `queryMembers` takes one too. The client's `uploadImage` and `uploadFile` and the channel's `sendFile` and `sendImage` take `axiosRequestConfig`. `createReminder`, `updateReminder` and `deleteReminder` put `messageId` into the path unencoded;
  - no current step reaches that argument. The matrix's 132 cases pass `validate`, and their `call` steps give these methods at most three positional arguments (the client's `search` three, `queryUsers` one; the channel's `queryMembers` one, `sendFile` and `sendImage` three), which never reach the request-options position. No step calls a reminder method;
  - the harness's own code also sends `call` ops, outside the matrix, which `validate` does not see: the controls, the setups and the families in `proof_run.py`, `mechanisms.py` and `i2a.py`. Of the methods above, it calls only `queryMembers` (`proof_run.py:854`, `:2752`) and `queryUsers` (`:2443`), each with one argument. So nothing sets a request option today;
  - `README.md:398` and C4's own record ("C4's own review", the re-check of `112011f`: "only a `call` of a client URL method, which `validate` refuses, could set them") state the claim the review disproves.
- **In the class: agreed, narrowly,** for the reason the review gives: a harness-authored step, or the harness's own code, could reach what the recorded mitigation says it cannot. The runner's host and path checks still apply to every HTTP request. What would pass them is a request-rewriting header that Stream's server or edge honours, which is not known.
- **Nit 2, confirmed:** `runner.cjs:250` sets `maxRedirects = 0` in the interceptor. In axios 1.20.0, `lib/adapters/http.js` (`:1051`) then uses the native `http` or `https` transport, not follow-redirects, unless the request names its own `transport`, and `lib/adapters/fetch.js` (`:478`) sets `redirect: 'manual'`. The manager did not try the review's offline-test technique.
- **Nit 3, confirmed:** ADR 0003's condition (c) says the limit "stands until P06.1-C4", and the architecture document's section 4 (c) gives finding 2 "for P06.1-C4". Section 5 already says correctly that the harness's fuller comparison runs at its next live use and that no live read has made it yet.
- **Nit 4, confirmed:** both `configure --apply` paths write the record (`cli.py:335`, `:421`) before `outcome.finish()` (`:340`, `:427`), so an error raised by the write replaces the stop.
- **Nit 5, confirmed:** `test_the_signal_is_read_from_the_ledger_not_the_exception` (`tests/test_cli.py:816`) replaces the stop with a Ctrl-C, which alone skips the re-read. The reversal of the ledger rule ("C4 nit 8: the signal is read from the ledger's recorded signals, not the exception") names only that test, which then fails on the record's label, not on a request sent.
- **Hosted CI:** PR run [36345354254](https://github.com/amthorn78/glow-dating-app/actions/runs/36345354254) on `f17b111`: seven jobs, all success; "Stream proof checks" ran every step, and the gate passed. Push run 36336214481 is as the manager recorded it.
- **Not re-run by the manager:** the session's reversal run, its differential normalization test and its SDK inventory. Its tests, lint, mypy and reversal summary (378, none "not demonstrated"; 456, 49 and 3) match C4's record and the manager's own run. The manager checked the methods finding 1 names in the SDK itself.
- **The environment check:** on the session's default PATH, `node` was `/opt/node22/bin/node` v22.22.2 and npm 10.9.7. The prompt expected the pinned toolchain from `$HOME/.local/bin`; the session put it first on PATH for every check. The C5 prompt states this as an instruction.

#### Disposition

- **C4 stands, with finding 1 to fix.** Its other fixes are confirmed, and no recorded result changes.
- **Finding 1 is in the review prompt's class,** narrowly. So an offline correction pass, **P06.1-C5**, fixes it before P06.1 closes. Required:
  - **`validate`** refuses every `call` step outside an explicit allowlist of (target, method, maximum positional arguments) that holds exactly what the current matrix uses, on both targets. Another method, another target, an argument that would reach a request-options position, and the reminder methods all lie outside it. A test for each kind, and a reversal;
  - **the manager's addition:** the runner also refuses a request carrying a request-rewriting header (`X-HTTP-Method-Override`, `X-HTTP-Method`, `X-Method-Override`, `X-Original-URL`, `X-Rewrite-URL`), in any letter case, as it refuses the forwarding headers: before the budget, neither sent nor counted, error kind `refused`. `validate` sees only the matrix, and the harness's own code also sends `call` ops; this closes the residual for every caller. Neither stream-chat 9.53.0 nor axios 1.20.0 sends any of these headers. A test that drives the real runner, and a reversal;
  - **the records:** `README.md:398` and C4's limits bullet in its section of this record are corrected in place, marked "(corrected in P06.1-C5; the C4 review's finding 1)". They say what `validate` covers, what the runner now refuses, and what remains (a per-request `proxy`, `socketPath` or adapter, none of which gets past the runner's check).
- **C5 also takes nits 2, 4 and 5,** because it runs anyway. Each gets a test that fails without the fix, and a reversal:
  - **nit 2:** an offline test that every request leaves the interceptor with `maxRedirects` 0;
  - **nit 4:** a failed record write after a signal keeps the stop: exit 3, and a line that names the signal;
  - **nit 5:** a variant of the ledger test in which an ordinary error replaces the stop, and no re-read is sent. The ledger rule's reversal must fail it.
- **Nit 3 is the manager's, in this batch.** ADR 0003's condition (c) and the architecture document's section 4 (c) now say that C4 extended the harness's comparison. They also say that the other roles and settings being unchanged rests on Stream's documentation until a live read, which is a question for the Dev Manager's close-out consultation.
- **The review's disagreement with the manager's README-limits disposition is accepted;** it is finding 1.
- **C5 and its exact-head review land before any further live use of the harness,** including a read the close-out consultation may weigh. The exact-head review of C5 is P06.1's final delta review, with the same bound as this one; the economics discovery follows it.

## P06.1-C5 corrections

Nathan ran this session from revision 1 of the [C5 correction prompt](../../ephemeral/2026-09-27-p06-1-c5-correction-prompt.md), from commit `438d047046e275e2a781937cc7f8e51f2b1a0bf6` (App Manager 5's manager branch `claude/magical-wozniak-yfmmx2`), on the session branch `claude/zealous-gauss-bgnir3`. It made no Stream call and no call to any other provider, and ran none of the harness's live commands. Commits:

- `1e65ace`: the fixes;
- `fc489d9`: a test now checks the rule its name gives;
- `61eae94`: the record corrections;
- `11b5771`: what C5's own review found;
- the records commit that adds this section, the branch head named in the session's report.

The code head is `11b5771`.

### Environment and start gate

- None of `DATABASE_URL`, `HD_API_KEY`, `GEO_API_KEY`, `STREAM_APP_ID`, `STREAM_API_KEY` or `STREAM_API_SECRET` was present (names checked only).
- The default PATH already finds the pinned toolchain first: `/root/.local/bin` is its first entry. `node`, `npm`, `npx` and `python3.12` all resolve there, as they do with `$HOME/.local/bin` put first, which every harness process had. Versions: node v24.19.0, npm 11.9.0, npx 11.9.0, Python 3.12.14.
- The start gate passed:
  - `git fetch origin claude/magical-wozniak-yfmmx2`;
  - `git merge --ff-only 438d047…` fast-forwarded the session branch from `0f45e64` (`main`);
  - `git rev-parse HEAD` printed `438d047046e275e2a781937cc7f8e51f2b1a0bf6`;
  - `git diff --stat c83bedf… HEAD -- proofs/stream-chat/ .github/` printed nothing.
- Installs and offline checks ran in clean processes (`env -i` with the path, home and locale; the proxy and CA variables passed by reference for the installs):
  - `python3.12 -m venv .venv`;
  - `pip install --require-hashes -r requirements-dev.lock`;
  - `pip check` ("No broken requirements found.");
  - `npm ci --ignore-scripts` ("found 0 vulnerabilities").

  No dependency file changed.

### The review's items

Paths are under `proofs/stream-chat/`; line numbers are at the code head, `11b5771`. Each fix has an offline test that fails without it and a reversal in `checks/fix_reversals.py` (the "C5 …" entries).

- **Finding 1, fixed: both the allowlist and the manager's addition.**
  - **`validate`.** `glow_stream_proof/matrix.py:2068`, `CALL_ALLOWLIST`, holds the 39 (target, method) pairs that the matrix's `call` steps use: 24 on the channel and 15 on the client. Each pair has the most positional arguments any step passes. `validate` calls `_call_refusal` (`:2114`) for every `call` step (`:2194`), after C4's `_product_reach` (`:2188`). It refuses:
    - a target other than the client or a channel;
    - a method that is not a name (`:2124`, from C5's own review, below);
    - the client's reminder methods (`REMINDER_METHODS`, `:2111`: `createReminder`, `updateReminder`, `deleteReminder`), whatever the allowlist holds, because they put a caller value into the path unencoded;
    - a method not on the allowlist;
    - arguments that are not a list (`:2134`);
    - more positional arguments than listed (`:2136`).

    The client's URL methods keep C4's refusal and message, and a `get` of a product path keeps its rule. `validate(all_cases())` is `[]`.
  - **Why the counts suffice**, from stream-chat 9.53.0 as installed, read offline:
    - for every listed method, each argument up to its count goes into the request's body, its payload, or a path segment the SDK encodes (`encodeURIComponent`, or `_channelURL`);
    - the method's first request-options argument lies beyond its count.

    The request-options positions the review names:
    - listed: the client's `queryUsers` and `search` (4th); the channel's `queryMembers` (4th); the channel's `sendFile` and `sendImage` (5th);
    - not listed: the client's `searchUserGroups` and `searchRoles` (2nd), `queryChannelsRequestWithResponse` (4th), and `uploadFile` and `uploadImage` (5th).

    `queryChannels` is listed with 3 and passes only its 4th argument's `signal` to the request. C5's own review read every entry again and agreed.
  - **The runner.** `client/runner.cjs:140`, `REWRITING_HEADERS`. `productRequestRefusal` (`:203`) refuses a request carrying any of these, in any letter case (`:222`):
    - `X-HTTP-Method-Override`;
    - `X-HTTP-Method`;
    - `X-Method-Override`;
    - `X-Original-URL`;
    - `X-Rewrite-URL`.

    It does so as it refuses the Host (`:216`) and forwarding (`:218`) headers. It runs in the request interceptor (`:271`), before the budget. A refused request is neither counted, sent nor recorded; its error kind is `refused`, whatever op sent it.
  - **Header names are read as they are sent** (`sentHeaderName`, `:251`), for every name, the per-method sections' too (`headerNames`, `:258`):
    - **trimmed (`:252`), found by C5 in its own reading.** Names were compared lower-cased but untrimmed, while axios trims them before sending (its http adapter's `AxiosHeaders.from(config.headers).normalize()`). So `" Host"` and `"X-Forwarded-Host\t"` passed C4's check, and axios would have sent them as `Host` and `X-Forwarded-Host`: before the fix, each reached error kind `budget`, not `refused` (shown offline);
    - **with an underscore read as a hyphen (`:253`), from C5's own review.** `X_HTTP_Method_Override` or `X_Forwarded_Host` passed the check, and some servers read an underscore in a name as a hyphen.

    Both change only which spellings of an already-refused header are refused. A header of a caller's choosing is reachable only through a request-options argument (see "Deviations and limits").
  - **Neither package sends a refused header.** `test_neither_stream_chat_nor_axios_names_a_rewriting_header` reads every file of `node_modules/stream-chat` (9.53.0, 265 files) and `node_modules/axios` (1.20.0, 89 files). No file names:
    - any of the five headers, in any letter case;
    - any refused name in its underscore spelling.

    No chat case is affected: an ordinary chat request still reaches the budget, and C4's tests of the 18 product cases' steps still pass the check.
  - **Tests.**
    - `tests/test_matrix.py`, `CallAllowlistValidationTest` (`:385`, 10 tests):
      - the allowlist equals the matrix's use, and every case validates;
      - an unlisted client method (`searchUserGroups`, `queryChannelsRequestWithResponse`, `searchRoles`, `uploadFile`, `uploadImage`, `getUnreadCount`);
      - an unlisted channel method (`markRead`, `hide`, `stopWatching`, `sendAction`);
      - one positional argument too many, for every entry (each valid at its limit);
      - the review's positions, with a rewriting header in the request options;
      - each reminder method, refused also when patched into the allowlist;
      - another target;
      - a method that is not a name (`["createReminder"]`, an object, `None`, a number);
      - arguments that are not a list (a string, an object, a number);
      - C4's two rules: a client URL method is refused as one, and a `get` of a product path is refused while a chat `get` validates.
    - `tests/test_runner.py`, `RequestHeaderTest` (`:656`, 5 tests), with the real runner, a zero budget and an unreachable proxy (`HTTPS_PROXY=http://127.0.0.1:1`):
      - error kind `refused`, nothing counted or sent, for:
        - each of the five headers;
        - `x-REWRITE-url`, in another letter case;
        - a padded name;
        - the channel's `queryMembers` and the client's `queryUsers`, with a request-options object in the 4th position;
      - an ordinary chat request still reaches `budget`;
      - padded names (`" Host"`, `"X-Forwarded-Host\t"`, `" X-Original-URL "`): `refused`;
      - underscore spellings (`X_HTTP_Method_Override`, `x_original_url`, `X-HTTP_Method`, `x_method-override`, `X_Rewrite_URL`, `X_Forwarded_Host`, `x_original_host`): `refused`;
      - axios's own `AxiosHeaders` trims the names the interceptor saw before the adapter sends them;
      - the package scan above.
  - **Reversals:**
    - "C5 finding 1: validate refuses a call step outside the allowlist";
    - "C5 finding 1: a listed method takes no more positional arguments than listed";
    - "C5 finding 1: a reminder method is refused whatever the allowlist holds";
    - "C5 finding 1: a call step's arguments must be a list";
    - "C5 finding 1: the runner refuses a request-rewriting header, whatever op sent it";
    - "C5: a header name is read as axios sends it, trimmed";
    - "C5 review: a header name's underscores are read as hyphens";
    - "C5 review: validate refuses a call whose method is not a name".
- **Nit 2, fixed.** `tests/test_runner.py`, `MaxRedirectsTest` (`:817`), loads `client/runner.cjs` with a stub `stream-chat` in `require.cache`, as the runner places its WebSocket for `isomorphic-ws`.
  - It captures the one request interceptor the runner registers.
  - It calls the interceptor with three configs:
    - a chat `post` without `maxRedirects`;
    - a `get` with 5;
    - a `post` with a `baseURL` and 21.
  - Each leaves with `maxRedirects` 0 (`client/runner.cjs:275`).

  Reversal: "C5 nit 2: every request leaves the interceptor with maxRedirects 0".
- **Nit 4, fixed.** `glow_stream_proof/cli.py:185`, `_write_record`, writes both `configure --apply` paths' records: `:388`, the general apply, and `:475`, the scoped apply. `_Applied.stop(ctx)` (`:148`) returns what must reach `main`, and `finish(ctx)` (`:172`) raises it.
  - **When the record's write raises** (the leak check refuses the record, or the disk write fails), a line is printed:
    - "the configuration record was not written: `<type>`: `<error>`";
    - then "; a charge or limit signal was met: `<the ledger's first signal>`";
    - then, when what ended the apply is neither that signal nor a refused step (which `_apply` already printed), "; the apply stopped on `<type>`: `<error>`".
  - **Then the stop is raised with the write's error chained** (`raise stop from exc`, `:213`), so a signal exits 3. With no stop in flight, the write's error is raised, after the same line.
  - **After a signal, the signal's stop is what reaches `main` even when an ordinary error replaced it in flight** (`:162`, from C5's own review). Nit 4 requires exit 3 after a signal when the write raises. At `1e65ace`, a signal whose stop an ordinary error had replaced exited 1, whether or not the write failed. The ledger now decides this, as it decides the re-read: the ledger's first signal reaches `main`, with the replacing error chained (`raise stop from ended`, `:180`). Only a Ctrl-C is kept instead, as C4 decided.
  - Nothing is sent either way: the write comes after the apply and after the re-read decision.
  - Tests: `tests/test_cli.py`, `RecordWriteAfterASignalTest` (`:1053`, 8 tests):
    - a 402 on the second write, then a record write refused by the leak check (`LeakRefused`) or failing on the disk (`OSError` 28), in each path. The `GuardrailStop` with "HTTP 402" reaches the caller, and its `__cause__` is the write's error. The one line names both, and no request follows the signal;
    - the same with an ordinary error in place of the stop: the ledger's signal leaves, and the line also names the error;
    - `main` exits 3 and prints "guardrail stop: …" for both commands. It does so also when an ordinary error replaced the stop, with the write succeeding and failing;
    - without a signal, the write's error is raised and printed.

    Also `ConfigureRecordTest.test_a_signal_in_the_reread_whose_stop_an_error_replaced_still_leaves` (`:877`): after a refused step, a signal in the re-read whose stop an error replaced leaves (exit 3), not the refusal (exit 1).
  - Reversals:
    - "C5 nit 4: a failed record write after a signal keeps the stop (the general apply)";
    - "C5 nit 4: a failed record write after a signal keeps the stop (the scoped apply)";
    - "C5 nit 4: the write's error is chained to the stop";
    - "C5 review: after a signal, its stop reaches main whatever replaced it, except a Ctrl-C".
- **Nit 5, fixed.** Two variants of the prompt's test, in `tests/test_cli.py`, `ConfigureRecordTest`:
  - `test_the_signal_is_read_from_the_ledger_when_an_ordinary_error_replaced_it` (`:849`): the scoped apply, a 402;
  - `test_general_the_signal_is_read_from_the_ledger_when_an_ordinary_error_replaced_it` (`:864`): the general apply, a 429 with code 9.

  In each, the signal is met on the second write, and an ordinary `RuntimeError` replaces its stop. The tests check that:
  - no request follows the signal, so no re-read was sent;
  - the record's `after` is "after-state not read: a charge or limit signal was met", and its `failure` names the error;
  - since C5's own review, the ledger's signal is what leaves, with the error chained. `GuardrailStop` is a `RuntimeError`, so the test checks the identity.

  Both are in the ledger rule's reversal, "C4 nit 8: the signal is read from the ledger's recorded signals, not the exception". It fails them on the requests sent: `15 != 10` (scoped) and `18 != 10` (general).

### C5's own review

A read-only sub-agent of this session reviewed the code diff at `1e65ace` under the prompt's rules: no network, no environment value, no change, and no run of `fix_reversals.py`. It exported the commit with `git archive` and tested it in a scratch directory, because the working tree was being edited meanwhile. It ran the unit tests (564, OK), Ruff, format, mypy and `node --check`, all clean. It applied every C5 reversal, and the extended C4 nit 8 one, in scratch, and each failed for the right reason. It then drove the real runner offline and ran every `configure` combination through `main`.

**Blocking: none.**

**Should-fix:**
1. **The runner's refused headers are a list, and some spellings and headers pass it.**
   - Underscore spellings (`X_HTTP_Method_Override`, `x_original_url`, `X_Forwarded_Host`) passed, and some server stacks read `_` as `-`. **Fixed at `11b5771`:** names are compared with an underscore read as a hyphen, as described under finding 1.
   - Other routing headers (`X-Forwarded-Prefix`, `X-Forwarded-Proto`, `X-Original-Method`) pass. **Recorded, not changed** (README, "Added in P06.1-C5"). They are not among the headers the manager's addition names. A header of a caller's choosing can be set only through a request-options argument, which no case step can pass after C5 and the harness's own `call` ops do not.
   - The reviewer's stronger fix, refusing every header name outside those stream-chat and axios set before the interceptor, is a change of design. It is for the manager to take up. The reviewer's own classification was "not class A today".
2. **An ordinary error that replaced a signal's stop exited 1, not 3**, with or without a failing record write. The new nit 5 tests' `assertRaises(RuntimeError)` could not tell the two apart, because a `GuardrailStop` is a `RuntimeError`. **Fixed at `11b5771`**, as described under nit 4: nit 4 requires exit 3 after a signal when the write raises, and the README already said that the command exits through the guardrail stop after a signal.
3. **The committed README at `1e65ace` still described the code before C5.** It was already corrected at `61eae94`, which the review did not cover.

**Nits:**
- **A `method` that is a list or an object made `_call_refusal` raise `TypeError` instead of returning a problem.** The runner looks a method up by its string form, so `["createReminder"]` would reach the reminder method. The tests failed closed. **Fixed at `11b5771`** with a test and a reversal. Reason: `validate` should refuse such a step, not crash on it.
- **If `ctx.say` itself raised in `_write_record` with no stop in flight, the say's error left instead of the write's**, and the docstring said otherwise. The write's error is still its context, so nothing is lost. **The docstring now says so**; the behaviour is unchanged.
- **The runner's check covers headers only.**
  - The non-header request options (`adapter: "fetch"`, `socketPath`, `proxy`, `httpVersion: 2`) pass it. They stay recorded as residuals, as the prompt requires.
  - Enforcing the allowlist's argument counts in the runner's `call` op, so that the harness's own code is covered at run time, is recorded as a proposal, not made. It would need its own table of the harness's `call` ops, and none of them passes a request option.
  - The "arguments are not a list" branch had no test. **It has one now**, with a reversal.

**What the reviewer checked and found sound:**
- every allowlist entry against `node_modules/stream-chat/dist/cjs/index.node.js`, and that the reminder methods are the only directly callable client methods that put a caller value into the path unencoded;
- that names are trimmed exactly as axios 1.20.0 trims them;
- that every header form is merged before the interceptor runs;
- that no SDK header name collides with the refused lists;
- every `configure` combination through `main`.

It did not run `checks/fix_reversals.py` (this section's "Checks" item 5 does), and it made no network or live check.

**The C4 reversal "C4 re-check 1" now fails only its Ctrl-C test.** Since `11b5771`, the ledger also sends a signal met by the re-read to `main`, so with `later` reverted the signal test passes. The Ctrl-C test still fails ("KeyboardInterrupt not raised"), so the reversal is demonstrated; a comment in the table says so.

### Records corrected

- **`proofs/stream-chat/README.md`:**
  - **`:397`, corrected in place** and marked "(corrected in P06.1-C5; the C4 review's nit 2 …)": `maxRedirects: 0` now has an offline test. The WebSocket-host statement is kept.
  - **`:398`, corrected in place** and marked "(corrected in P06.1-C5; the C4 review's finding 1 …)". It says:
    - which stream-chat methods take a request-options argument;
    - what `validate` covers: the matrix's steps, on the allowlist, with no reminder method; the harness's own `call` ops pass no request option either;
    - what the runner refuses: the five rewriting headers, in any letter case and with an underscore for a hyphen, on every request, whatever sent it; neither package sends one;
    - what remains: a per-request `proxy` or `socketPath`, `adapter: "fetch"` or `httpVersion: 2` (the fetch-adapter statement is kept), and JSON nested two levels deep in a query value. None gets past the runner's host and path checks. (The README's nested-JSON item is corrected by App Manager 5 after the exact-head review of C5, its nit 1: a `product` step's `params` can carry it too.)
  - **Brought into line:**
    - "Nothing else reaches Video or Feeds" (`:281`): the rewriting headers, how header names are read, `validate`'s allowlist, and the refusal of a method that is not a name or arguments that are not a list;
    - the scoped `configure --apply` bullet (`:336`): nit 4, and what reaches `main` after a signal;
    - the configure-record limit (`:400`): a re-read failure after a refused step exits 1 unless a signal was met;
    - the file table (`:28`) and "Checks (offline)" (`:109`): the reversal script covers C4 and C5 (`:28` had not named C4 either).
  - **"Added in P06.1-C5", three limits:**
    - `validate` runs offline only, and the allowlist is exactly the matrix's use;
    - a configure record whose own write raises after a signal is not written;
    - the header check names the headers it refuses.
- **This record:** one bullet of "P06.1-C4 corrections", corrected in place: the one under "C4's own review" on the re-check of `112011f` (line 3600). It is marked "(corrected in P06.1-C5; the C4 review's finding 1: …)" and says what `validate` covers, what the runner refuses and what remains, as the README does. Every other part of the record is byte-identical to `438d047`, the manager's verification of C4 and the exact-head review of C4 included. This section is appended at the end.

### Checks

1. `git diff --check 438d047046e275e2a781937cc7f8e51f2b1a0bf6 HEAD`: no output, exit 0.
   - `git diff --name-only 438d047… HEAD`: 9 paths, all owned. They are this record and 8 under `proofs/stream-chat/`: `README.md`, `checks/fix_reversals.py`, `client/runner.cjs`, `glow_stream_proof/cli.py`, `glow_stream_proof/matrix.py`, `tests/test_cli.py`, `tests/test_matrix.py` and `tests/test_runner.py`.
   - No dependency file, lock, `.npmrc`, `pyproject.toml` or committed baseline changed. Every file is mode 100644, and there is no symlink.
2. **Classification** used the trusted policy from `origin/main` (`0f45e64`, sha256 `dec69a26…`), extracted to a directory outside the tree and run as `python3 -I …/change_scope.py --base 438d047046e275e2a781937cc7f8e51f2b1a0bf6 --head <head> --merge-base`.
   - It gave `{"full": true, "reason": "behavior-or-empty", …}` at `61eae94`, and again at `11b5771`, the last commit before this section: full scope, as expected, with one merge base (`438d047`) and the 9 paths above.
   - This section's commit adds Markdown only.
3. **Installs:** as above, in the working tree, and again in scratch exports of `438d047`, `fc489d9` and `11b5771` for the full reversal runs.
4. **Offline checks** at `11b5771`, in the working tree and in the scratch export, with the same results:
   - unit tests: `Ran 570 tests`, `OK` (`Ran 543 tests … OK` at the start; 564 at `1e65ace`);
   - Ruff: "All checks passed!" and "55 files already formatted";
   - mypy: "Success: no issues found in 53 source files";
   - `node --check` OK for `error-info.cjs`, `product-op.cjs`, `request-log.cjs` and `runner.cjs`;
   - `checks/run_plan.py` with an empty ledger (no `.work` directory): "run plan: fits", exit 0.
5. **Fix reversals** (`checks/fix_reversals.py`, from a scratch copy outside the tree):
   - **at the start:** "reversals: 378, not demonstrated: 0", exit 0, 23:00:43 to 23:28:35 UTC. The failure reasons read 456 `AssertionError`s and 49 errors, with 3 test processes stopped by design (Ctrl-C);
   - **at `11b5771`, the code head: "reversals: 391, not demonstrated: 0", exit 0, 00:06:23 to 00:34:15 UTC** (378 at the start, and 13 C5 entries). Every row is OK.
     - The failure reasons read 505 `AssertionError`s and 50 errors, with 3 test processes stopped by design (Ctrl-C), as at the start.
     - The one error beyond the start's is the new method-name reversal's `TypeError: unhashable type: 'list'`: the crash that rule removes.
     - None failed through a syntax, import or name error;
   - **subset runs along the way:**
     - the 9 C5 entries at `1e65ace`: "not demonstrated: 0";
     - the 36 C4 entries at `1e65ace`: "not demonstrated: 0";
     - 38 entries on the working tree that became `11b5771` (every C5 entry, and the C4 entries on the same code): "not demonstrated: 0";
   - **stopped, not a result:** a full run at `fc489d9`, stopped by this session after 295 of 387 entries, when `11b5771` superseded it; none "not demonstrated" by then;
   - **each new reversal's failure reason** (from the run at `11b5771`):
     - "C5 finding 1: validate refuses a call step outside the allowlist": its six tests fail on the problems returned, for example `Lists differ: [] != ["X-call: a call of the channel's markRead, which is not on the call allowlist"]` and `0 != 1 : queryUsers`;
     - "… a listed method takes no more positional arguments than listed": `Lists differ: [] != ["X-call: a call of the channel's addMembe[104 chars]ble"]` and `0 != 1 : queryUsers`;
     - "… a reminder method is refused whatever the allowlist holds": the reminder is refused only as unlisted, `[… which is not on the call allowlist"] != [… which puts a caller value into the request path unencoded"]`;
     - "… a call step's arguments must be a list": `Lists differ: [] != ["X-call: a call of the client's queryUsers whose arguments are not a list"]`;
     - "… the runner refuses a request-rewriting header, whatever op sent it": `'budget' != 'refused'`, in ten subtests;
     - "C5: a header name is read as axios sends it, trimmed": `'budget' != 'refused'`;
     - "C5 review: a header name's underscores are read as hyphens": `'budget' != 'refused'`, in seven subtests;
     - "C5 review: validate refuses a call whose method is not a name": `TypeError: unhashable type: 'list'`, the crash the rule removes (an error by design; the reverted file loads);
     - "C5 nit 2: every request leaves the interceptor with maxRedirects 0": `Lists differ: ['unset', 5, 21] != [0, 0, 0]`;
     - "C5 nit 4: … (the general apply)" and "(the scoped apply)": `LeakRefused('refused output: contains a known secret') is not an instance of <class 'glow_stream_proof.usage.GuardrailStop'>`, the same for `OSError(28, 'No space left on device')`, and `OSError(28, 'No space left on device') != 3` from `main`;
     - "C5 nit 4: the write's error is chained to the stop": `None is not OSError(28, 'No space left on device')`;
     - "C5 review: after a signal, its stop reaches main whatever replaced it, except a Ctrl-C": `RuntimeError('an error in place of the stop') is not GuardrailStop('server PUT …: HTTP 402; stopping at once')`, `BaseException not raised` (the refused step's exit 1) and `RuntimeError('an error in place of the stop') != 3` from `main`;
     - the ledger rule's reversal, with the two nit 5 tests: `15 != 10` and `18 != 10`, the requests sent after the signal.
6. **Secret scan** of the whole diff `438d047..11b5771` (88,234 bytes). The added lines hold none of:
   - a JWT-shaped string;
   - an email address;
   - a private-key block;
   - an AWS-style, GitHub or Slack token;
   - a TLS-weakening setting;
   - an environment dump;
   - a secret assignment.

   The 29 long token-like strings are 28 test names and one SDK method name (`queryChannelsRequestWithResponse`). The scan could not look for the application's API key, because its variable is absent (OD-28); no added line holds a 12-character string mixing lower-case letters and digits.
7. **Foundation, on this branch:**
   - run 369 on `1e65ace` ([36358644511](https://github.com/amthorn78/glow-dating-app/actions/runs/36358644511)) succeeded;
   - run 370 on `61eae94` ([36359890081](https://github.com/amthorn78/glow-dating-app/actions/runs/36359890081)) succeeded: all seven jobs, "Stream proof checks" included, every step success;
   - **run 371 on the code head `11b5771`** ([36360951436](https://github.com/amthorn78/glow-dating-app/actions/runs/36360951436)), 00:06:40 to 00:12:50 UTC: all seven jobs success.
     - Change scope, API checks, API artifact checks, API mobile smoke, and Mobile checks (the rendered suite included).
     - "Stream proof checks" ran, not skipped, and every step succeeded: the hash-locked install, `pip check`, `npm ci --ignore-scripts`, the tests under `env -i`, Ruff, format, mypy, `node --check` on every `.cjs` file, and `checks/run_plan.py`.
     - The Foundation gate.

   This records commit is Markdown only. It was pushed after run 371 finished, so it did not cancel that run; its own run is in the session's report. Nothing was re-run or dispatched.

### Deviations and limits

- **Beyond the review's items, C5 fixed three things**, each with tests and a reversal:
  - the header-name trim, found in its own reading;
  - the underscore spelling, from its own review;
  - a method that is not a name, from its own review.

  It also changed what reaches `main` after a signal (its own review's should-fix 2). That serves nit 4's requirement that a signal still exits 3 when the record's write raises.
- **The reminder methods have a rule of their own** rather than only being absent from the allowlist, so that an addition to the allowlist cannot admit them. A test patches one in, and it is still refused.
- **Nit 5 has two variants**, one per `configure --apply` path, where the prompt asked for one.
- **Nit 4's printed line names the ledger's signal as well as the write's error**, and what ended the apply when that is neither. A Ctrl-C that replaced the signal's stop still reaches `main`, as C4 decided; the line names the signal, and nothing is sent.
- **`validate` runs offline only.** It is called by the unit tests, and so by the Foundation job, never by a live command; a live command relies on the offline checks having passed at its head. The allowlist is exactly today's matrix: a new case with another method or more arguments fails the tests until the table changes.
- **The runner refuses named headers only.** Other routing headers pass its check. The non-header residuals (a per-request `proxy` or `socketPath`, the fetch adapter or HTTP/2, JSON nested two levels deep) do too. All but the nested JSON are reachable only through a request-options argument, which no matrix step can pass after C5 and no harness `call` op passes; a `product` step's `params` can carry JSON nested two levels deep (corrected by App Manager 5 after the exact-head review of C5, its nit 1). None gets past the runner's host and path checks. A per-request `proxy` would send the checked request, with its token, through the proxy it names; that is recorded, not changed.
- **Nothing here is exercised live.** No live run remains in P06.1.

### What the final delta review must know

- **Rules that changed.**
  - `validate` refuses every `call` step outside `CALL_ALLOWLIST` (target, method and a maximum of positional arguments). It also refuses:
    - the client's reminder methods, always;
    - a method that is not a name;
    - arguments that are not a list.
  - The runner refuses the five request-rewriting headers on every request, before it is counted or sent (error kind `refused`). It reads every header name trimmed, lower-cased and with an underscore as a hyphen: the Host and forwarding headers too.
  - `maxRedirects: 0` has an offline test.
  - After a charge or limit signal, the ledger's signal is what reaches `main` (exit 3), whatever replaced its stop in flight; only a Ctrl-C is kept instead. A `configure --apply` record write that raises keeps that stop, with the write's error chained and a line naming both.
- **Not yet exercised live:**
  - every C5 fix;
  - in particular the header refusal and the header-name reading on a live run's chat requests (the tests show no chat case sends such a header);
  - nit 4's path, which needs a failing write after a live signal.
- **For the delta review:** C5's change is `438d047..<head>`. The code commits are `1e65ace`, `fc489d9` (a test and the reversal table) and `11b5771`. The reviewer's working files stayed in this session's scratch directory.

### Manager verification of C5 (App Manager 5, 28 September 2026)

App Manager 5 checked the relayed report against the pushed branch. The manager made no call to Stream.

- **Identity:**
  - branch `claude/zealous-gauss-bgnir3`, head `1a5f58aec87cacfdd1dc32c893467f8f00e9ac7e`, tree `da7d7f8e9f8cb25298b2b74731caed9c80169d29`, as reported. Five commits on the start `438d047`, with one merge base (`0f45e64` with `main`). The code commits are `1e65ace`, `fc489d9` and `11b5771`; `61eae94` and `1a5f58a` change only Markdown. The code head is `11b5771`;
  - 9 files, +1,260 and −37: 8 under `proofs/stream-chat/` and this record. Every path is owned. No dependency file, lock, `.npmrc`, `pyproject.toml`, committed baseline or workflow changed. Every file keeps mode 100644, there is no symlink, and `git diff --check` is clean;
  - this record: within its length at `438d047`, only line 3600 changed, the bullet the prompt named, marked "(corrected in P06.1-C5; the C4 review's finding 1 …)". C5's section follows the old last line. Every other line is byte-identical to `438d047`, the manager's verification of C4 and the exact-head review of C4 included.
- **Classification:** the trusted policy from `main` (`0f45e64`, sha256 `dec69a26…`), outside the tree, with `python3 -I` and full SHAs: `438d047` → `1a5f58a` is full scope (`behavior-or-empty`), 9 paths; `11b5771` → `1a5f58a` is `ordinary-docs-only` (this record only).
- **Code read,** the whole diff of the production code, about 200 changed lines:
  - **finding 1, `validate`:** `CALL_ALLOWLIST` holds 39 (target, method) pairs, 24 on the channel and 15 on the client, each with the most positional arguments a step passes. They are the ones the manager counted in the matrix when it verified the C4 review. `_call_refusal` refuses another target, a method that is not a string, the client's three reminder methods whatever the allowlist holds, a method not on the list, arguments that are not a list, and more arguments than listed. C4's rules for the client's URL methods and a product `get` stand;
  - **the allowlist's safety,** spot-checked in stream-chat 9.53.0: `getMessage`, `getThread`, `getReplies`, `getReactions`, `partialUpdateMember`, `queryReactions`, `updateMessage`, `deleteMessage` and `sendReaction` encode every caller value they put into a path; `createPoll` puts none there, and `updateAIState` sends an event body only. The request-options positions of the listed methods lie beyond their counts;
  - **the manager's addition, the runner:** `REWRITING_HEADERS` names the five headers, and `productRequestRefusal` refuses them after the Host and forwarding headers, before the budget. `sentHeaderName` compares every name trimmed, lower-cased and with an underscore as a hyphen. Neither package sends a refused header: none of the 265 files of stream-chat 9.53.0 or the 89 of axios 1.20.0 names one, in either spelling;
  - **nit 4 and C5's own review:** `_Applied.stop` returns the ledger's first signal after any charge or limit signal, unless a Ctrl-C replaced it; without a signal the exit is what it was (1 for a refused step). The ledger's signals are kept in memory only (`UsageLedger.signals`; `load` restores the session counts, not the signals), so only this process's own signals count. `_write_record` prints a line and raises the stop with the write's error chained. One observation, for the exact-head review: a Ctrl-C during the record write itself, after a signal, leaves as the signal's stop (exit 3) with the Ctrl-C chained; nothing is sent either way;
  - **the reversal table:** 13 new C5 entries. The changes to C4's entries add tests or comments: "C4 re-check 1" now fails only its Ctrl-C test, because the new ledger branch also sends the signal case to `main`, and that branch has a reversal of its own.
- **Offline re-run,** in a scratch export of `1a5f58a`, in clean processes without any `STREAM_*` variable, the installs with the proxy and CA variables by reference:
  - `pip install --require-hashes -r requirements-dev.lock` and `pip check` ("No broken requirements found."); `npm ci --ignore-scripts` ("found 0 vulnerabilities");
  - unit tests: `Ran 570 tests`, `OK`. Ruff check: "All checks passed!"; Ruff format: "55 files already formatted"; mypy: "Success: no issues found in 53 source files". `node --check` on the four `.cjs` files: OK. `checks/run_plan.py` with an empty ledger: "run plan: fits";
  - `checks/fix_reversals.py`, from the export: "reversals: 391, not demonstrated: 0", exit 0, 00:42:29 to 01:13:38 UTC. Every row is OK: 505 failures on an assertion, 50 on the error the reverted fix causes, and 3 test processes stopped by Ctrl-C by design, none through a syntax, import or name error, as C5 reported. The one error beyond C4's 49 is the method-name reversal's `TypeError: unhashable type: 'list'`, the crash that rule removes;
  - each of the 13 C5 entries failed for the reason C5's section gives. "C4 re-check 1" failed its Ctrl-C test only ("KeyboardInterrupt not raised"), and the ledger rule's reversal failed the two nit 5 tests on the requests sent after the signal (`15 != 10`, `18 != 10`).
- **Secret scan** of the whole diff `438d047..1a5f58a` (119,481 bytes, the size the report gives): 0 JWT-shaped strings, email addresses, private-key blocks, AWS, GitHub or Slack tokens and secret assignments.
- **Hosted CI on C5's branch:**
  - push run 371 ([36360951436](https://github.com/amthorn78/glow-dating-app/actions/runs/36360951436)) on the code head `11b5771`: all seven jobs succeeded. "Stream proof checks" ran every step, not skipped, and Mobile checks ran the rendered suite;
  - runs 369 on `1e65ace` and 370 on `61eae94` succeeded. Run 372 on the head, a Markdown-only push, skipped the application jobs by design, and its gate passed: as the report says, not a pass of those jobs.
- **C5's own section,** read against the code and the runs: no slip found. Its secret scan covers `438d047..11b5771` (88,234 bytes); the report's covers the diff to the head.

#### Dispositions

- **C5 is verified and integrated** into the manager branch by fast-forward, at `1a5f58a`. Finding 1, with the manager's addition, and nits 2, 4 and 5 are fixed, each code fix with a test that fails without it and a reversal, as the prompt required. The record correction is the one the prompt named.
- **The deviations are accepted:**
  - **beyond the four items,** the header-name trim, the underscore spelling and the refusal of a method that is not a name. Each narrows what may be sent or validated;
  - **what reaches `main` after a signal:** the ledger's signal, whatever replaced its stop, except a Ctrl-C. It serves nit 4's requirement that a signal exits 3, and it changes no exit where no signal was met;
  - **the reminder methods' own rule, nit 5's two variants, and nit 4's line naming both the signal and what replaced it.**
- **The two proposals C5 recorded and did not make are not taken in P06.1:**
  - **an allowlist of header names in the runner,** in place of its list of refused names: the other routing headers can be set only through a request-options argument, which no matrix step can now pass and no harness `call` op passes. The exact-head review assesses whether any path reaches them;
  - **the argument counts enforced in the runner at run time:** the harness's own `call` ops are fixed in its code. The manager checked those that call a request-options method (`queryMembers` twice and `queryUsers` once, each with one argument).
- **The two pre-existing items C5 reported are recorded, not fixed here;** neither is in a correction class:
  - two test classes defined after `if __name__ == "__main__"` (`tests/test_stop_signals.py`, `tests/test_cleanup.py`), which `unittest discover` still finds;
  - `cmd_run`'s final results write, which, if it raises, exits through an uncaught error instead of the stop's code; nothing more is sent by then.
- **Not yet exercised live:** every C5 fix.
- **C5's exact-head review is next.** It is P06.1's final delta review, offline, of `1a5f58a`.

### Exact-head review of C5 (28 September 2026)

Nathan ran the review session from revision 1 of the [review prompt](../../ephemeral/2026-09-28-p06-1-c5-review-prompt.md) (records commit `8cac8d0`) on Opus 5.5 at extra high, and relayed its report to App Manager 5. The session committed and pushed nothing, and made no Stream call.

- **Verdict: approve.** C5's change and its records are sound, and P06.1 can close on them. There is no blocking or should-fix finding, and no finding falls in a class that needs another correction pass.
- **Three nits, none in that class.**
  - The records say JSON nested two levels deep in a query value is reachable only through a request-options argument, but a `product` step's `params` can carry it too.
  - A C4 clause that now matters only for a budget stop in the re-read has no test.
  - When no signal was met, `finish()` chains an apply failure to a later re-read error, replacing the failure's own cause.
- **The rest is confirmed.** The C4 review's items, and the items C5 or its own review found, are fixed. The review agrees with every one of the manager's dispositions, and would reconsider an allowlist of header names before the harness is used live again in P06.2.

#### The report, as relayed

The session's notes before its report, as relayed, verbatim:

> I'll start with the environment check (names only).
>
> Start gate passes. Now the three classifications.
>
> All three classifications match expectations. Now reading the C5 prompt and the diff.
>
> Now the code diff, file by file.
>
> Start gate and classifications pass; I'm now reading C5's evidence section before the code deep-dive.
>
> Now the manager's records at `8cac8d0`.
>
> Now the README's install and checks sections, and the parts C5 changed.
>
> Setting up a scratch export of the head for installs and checks (clean processes).
>
> Offline checks pass (570 tests). Starting the full fix-reversal run in the background while I read the code.
>
> While that runs, reading `cli.py`'s apply/stop logic in full.
>
> All checks pass so far (570 tests), and the full reversal run is going in the background. Having finished reviewing `cli.py`'s stop/exit logic, I'll now check the `validate` allowlist against the stream-chat 9.53.0 source.
>
> Now checking each allowlisted method against stream-chat 9.53.0's source. First the core request plumbing.
>
> Still reviewing: the channel methods on the allowlist check out so far; now the helpers they call (`_update`, `_sendMessage`, `_sendReaction`, `addFileToFormData`) and the client methods.
>
> Confirmed the allowlisted methods only place caller values into bodies, payloads, or encoded path segments. Now verifying whether the reminder methods are truly the only directly callable ones using an unencoded path value.
>
> Confirmed only the three reminder methods place unencoded caller values into a path, while the polls query methods put `userId` unencoded into the query string (no path steering, not allowlisted). Next I'll check the harness's own `call` ops outside the matrix.
>
> Progress: the harness's own `call` sites are being enumerated (proof_run, mechanisms, i2a). Checking the remaining ones, including control steps built from dicts.
>
> All harness `call` sites check out fine—none passes a request option, calls a reminder/URL method, or builds an unencoded path. Next I'll check the runner's header handling against axios 1.20.0 and the "nested JSON" issue.
>
> The README's allowlisted-method and header claims hold so far. Now the tests: `RequestHeaderTest`, `MaxRedirectsTest` and the matrix allowlist tests.
>
> Now a few adversarial header probes of my own against the real runner offline (zero budget, unreachable loopback proxy, as C5's tests do).
>
> Cases 4 and 7–11 check out, with 7 matching C5's recorded residual. I'll verify the remaining cases by spinning up a loopback-only HTTP server to see exactly what axios and Node send over the wire.
>
> Header handling checks out: NBSP-padded names are rejected by the runner, CRLF injection doesn't create extra headers, invalid names never leave Node, and null/false values plus other-method sections are correctly skipped. Moving on to the matrix and CLI tests now.
>
> The allowlist tests look right. Checking whether run-time placeholder filling could change a validated step's method or argument count.
>
> Now the CLI tests for nit 4/nit 5 and C5's own-review change.
>
> Tests are sound. Now the reversal table changes.
>
> I've read the reversal table. Now I'll test in a scratch copy whether the GuardrailStop clause in C4's `later` branch is redundant with C5's new ledger branch for signals, and whether it's untested for non-signal (budget) stops.
>
> Confirmed: with that clause removed, all 570 tests still pass. Checking the behavioural effect it guards (a non-signal budget stop in the re-read after a refused step).
>
> Confirmed as a test-coverage nit (no request is sent either way). Now verifying the evidence record's byte-identity outside C5's section and the one in-place correction.
>
> Record is byte-identical to `438d047` apart from line 3600 (the marked correction) and the appended section. Now checking every `file:line` C5's section cites.
>
> All 34 citations match. README line citations next, plus the counts C5's section states (39 pairs: 24 channel / 15 client; 10 + 5 + 1 + 8 tests).
>
> Everything cited matches. Now testing C5's recorded claim that JSON nested two levels deep is "reachable only through a request-options argument", using the `product` op's own `params` offline.
>
> Confirmed that a two-level nested JSON query value reaches the budget via the `product` op's own `params` and passes `validate`, so the "reachable only through a request-options argument" claim doesn't hold for that residual (C4's accepted residual is unaffected). Moving on to check scope, modes, and the secret scan.
>
> Secret scan clean (only a commit SHA, a path and an SDK method name match the broad patterns). Now hosted CI, read-only.
>
> Push run 371: all seven jobs success; "Stream proof checks" ran every step. Now PR27's latest pull-request run.
>
> PR27's latest pull-request run is 374 on `8cac8d0` (which contains the head). Checking its jobs.
>
> Both CI runs are green with the full "Stream proof checks" run complete. While reversals finish up, I'll run my own configure exit matrix through main offline using the test fakes.
>
> Every signal row shows nothing sent after the signal and exit 3 unless Ctrl-C replaced the stop, and a Ctrl-C during the post-signal write still exits 3. I'll now compare the no-signal rows against the pre-C5 code at `438d047`.
>
> No-signal exits are identical before and after C5; the only change is signal + failed write (exit 3 instead of an uncaught `OSError`), as intended. Checking the reversal run.
>
> Reversals are at 203 of 391. Meanwhile I'm checking README:398's list of stream-chat methods that take a request-options argument for completeness.
>
> Confirmed README:398's list matches exactly—those ten methods plus the URL methods pass a caller argument, while queryChannels only forwards `signal` and is unreachable at count 3. Now verifying the package-scan counts against C5 records.
>
> Package counts check out (265/89) and no refused or residual routing headers found. Next I'll verify `finish()`'s `raise stop from ended` behavior for the no-signal case where the apply fails with an ordinary error and the subsequent re-read also fails.
>
> Confirmed this is just a diagnostics-only nit — without a signal, `finish()` overwrites the apply failure's `__cause__` with the later re-read error, though exit code and record stay unchanged. Now waiting on the reversal run.
>
> While the run continues, a quick check of the two pre-existing items the manager recorded.
>
> Pre-existing items confirmed as the manager describes (test classes after the main guard still load under `discover`; `cmd_run`'s final write is outside C5's change). Checking the reversal run again.
>
> The run is progressing (its log is block-buffered). I'll wait on it with a monitor rather than end the turn.
>
> While the reversal run finishes, drafting the report. I'll resume when the monitor fires.
>
> Reversal run done: 391, none "not demonstrated", exit 0. Extracting the C5 entries' failure reasons, the "C4 re-check 1" row, the ledger-rule row, and the overall tallies.
>
> All 13 C5 entries fail for their stated reasons. Final check that I changed nothing in the repository.

The report, verbatim (its title in bold, its headings at level five):

**P06.1-C5 exact-head review: approve (final delta review)**

**Verdict: approve.** C5's change and its records are sound, and P06.1 can close on them. I found no blocking or should-fix finding. Three nits go into the records, and none falls in a class that needs another correction pass.

- **Prompt:** revision 1, from commit `8cac8d061d5719706aa2c712e58034dd0d36ec22`.
- **Head reviewed:** `git rev-parse HEAD` printed `1a5f58aec87cacfdd1dc32c893467f8f00e9ac7e`.
- **Environment:** none of `DATABASE_URL`, `HD_API_KEY`, `GEO_API_KEY`, `STREAM_APP_ID`, `STREAM_API_KEY` or `STREAM_API_SECRET` was present (names checked only).
- **Toolchain:** the default PATH already finds the pinned tools in `/root/.local/bin`: node v24.19.0, npm 11.9.0, npx, python3.12 3.12.14. I put `$HOME/.local/bin` first on PATH for every harness process anyway.
- **Start gate:** passed.
  - The merge base with `main` is one line, `0f45e648…`.
  - The records commit `8cac8d0` builds on the head.
  - `git diff --stat 438d047 HEAD`: 9 files, 1260 insertions, 37 deletions.

**Classification.** I used the trusted policy from `main` (sha256 `dec69a26…`), extracted outside the tree and run with `python3 -I` and full SHAs:

| Range | Result |
|---|---|
| `main` → head | `{"full": true, "reason": "behavior-or-empty", …}`, 145 paths |
| `c83bedf` → head | `{"full": true, "reason": "behavior-or-empty", …}`, 18 paths. The filter for non-Markdown files outside `proofs/stream-chat/` printed nothing |
| head → `8cac8d0` | `{"full": false, "reason": "ordinary-docs-only", …}`, 5 paths |

##### Findings, most severe first

**1. Nit (records): one residual's reachability is misstated.** Not in a correction class.
- **Where:** `proofs/stream-chat/README.md:398`, and the evidence record's C5 section at lines 4107 and 4191.
- **What they say:** "JSON nested two levels deep inside a query value" is "reachable only through a request-options argument".
- **What I found:** it is also reachable through the `product` op's own `params`, and through the `get` op's. `validate` passes such a step: `products.client_refusal` returns `None`. I showed this offline with the real runner (zero budget, unreachable proxy):
  - one level deep, `{"payload": "{\"ring\": true}"}`, is refused with "denied field (ring)";
  - two levels deep, `{"payload": "{\"a\": \"{\\\"ring\\\": true}\"}"}`, reaches the budget, so the runner would send it.
- **Why it is not in a class:** this residual is C4's, and C5 did not change the code. The C4 review assessed it as not reaching Video or Feeds, because Stream is not known to decode a JSON string nested inside a query value. No current case and no harness op carries it.
- **Suggested fix:** reword both records, for example: "reachable through a `product` or `get` step's `params` too; `validate`'s Python mirror does not parse nested JSON either". If the manager wants it closed in code, both checks would have to read JSON recursively.
- **Optional, same records:** line 3600's "What remains" names only `proxy`, `socketPath` and the adapter. The other routing headers (`X-Forwarded-Prefix` and similar) are recorded in the README and in C5's section, so a pointer to them would do.

**2. Nit (test coverage): one C4 clause no longer has a test.** Not in a class: no request is sent either way.
- **Where:** `glow_stream_proof/cli.py:158`, the `isinstance(later, GuardrailStop)` clause of `_Applied.stop`.
- **What changed:** C5's new ledger branch also sends a re-read signal to `main`. So this clause now matters only for a guardrail stop that is not a signal: the API-call budget stop, met by the re-read after a refused step.
- **Scenario:** I removed the clause in a scratch copy, and all 570 tests still passed. I then drove a budget `GuardrailStop` in the re-read after a 400:
  - at the head, the `GuardrailStop` reaches `main` (exit 3);
  - with the clause removed, the command returns 1.

  The budget refuses before sending, so nothing is sent in either case.
- **This answers the prompt's question on "C4 re-check 1".** The signal case is still covered, twice: by the `later` branch and by the ledger branch. So no single reversal can make `test_a_signal_in_the_reread_after_a_refused_step_still_reaches_main` fail. The ledger branch is shown by "C5 review: after a signal, its stop reaches main…", through `test_a_signal_in_the_reread_whose_stop_an_error_replaced_still_leaves`. Only the clause's remaining budget-stop case has no test.
- **Suggested fix:** add a test in which the re-read after a refused step raises a budget `GuardrailStop` (not one from `stop_at_once`) and must reach `main`, and add a reversal that removes only the clause.

**3. Nit (diagnostics): an exception chain is backwards when no signal was met.** Not in a class: the exit code and the record are unchanged.
- **Where:** `glow_stream_proof/cli.py:179–180`, the `raise stop from ended` in `finish()`, which also runs without a signal.
- **Scenario:** without a signal, the apply fails with an ordinary error, the re-read runs (it is allowed then), and the re-read fails too. `finish` then raises the apply's failure `from` the later re-read error. That shows the re-read as the "direct cause", and it overwrites the failure's own `__cause__`.
  - I showed this offline: a `ConnectionError` raised from an `OSError`. At `438d047` its cause is still the `OSError`. At the head it is the re-read's `RuntimeError`.
  - The exit code is unchanged, nothing is sent, and the record still keeps both `failure` and `reread_failure`.
- **Suggested fix:** chain only when the stop being raised is the ledger's signal, not the apply's own failure.

##### The C4 review's items and C5's own items

| Item | Status |
|---|---|
| **Finding 1, `validate` allowlist** | **Confirmed fixed.** Details below |
| **Manager's addition, rewriting headers** | **Confirmed fixed.** Details below |
| Nit 2, `maxRedirects` | Confirmed fixed. `MaxRedirectsTest` loads the real `runner.cjs` with a stub `stream-chat`, calls the one interceptor it registers, and gets `[0, 0, 0]`. Its reversal fails on `['unset', 5, 21]` |
| Nit 3 | The manager's own item. ADR 0003 was outside this review's scope and was not read |
| Nit 4, record write after a signal | Confirmed fixed. See the exit table below |
| Nit 5, the ledger-rule test | Confirmed fixed. Two variants; the ledger-rule reversal fails them on the requests sent (`15 != 10`, `18 != 10`) |
| C5: header names trimmed | Confirmed fixed |
| C5's review: underscore read as a hyphen | Confirmed fixed |
| C5's review: a method that is not a name | Confirmed fixed |
| C5's review: arguments that are not a list | Confirmed fixed |
| C5's review: the ledger decides the exit after a signal | Confirmed fixed |
| C5's review: the docstring on a failing print | Confirmed fixed |

**Finding 1, the `validate` allowlist.**
- `CALL_ALLOWLIST` has 39 pairs, 24 on the channel and 15 on the client. It equals what the matrix uses, and the test keeps it so. All 132 cases validate.
- I read every allowlisted method at its count in stream-chat 9.53.0. Each argument reaches only the body, the query payload, or a path segment that is `encodeURIComponent`-encoded; `_channelURL` encodes the type and ID too.
- No request-options position is reachable at these counts. `queryChannels` at 3 is safe: its fourth argument only forwards `signal`.
- A multi-line scan of the Channel and StreamChat classes finds only the three reminder methods putting a caller value into a path unencoded. The polls query methods put `userId` into the query string after `?`, which cannot change the path, and none of them is allowlisted.
- The README's list of methods that take a request-options argument is complete.

**The manager's addition, the rewriting headers.**
- The runner refuses them before the request is counted or sent, with error kind `refused`, whatever op sent it.
- My own offline probes against the real runner:

| Probe | Result |
|---|---|
| A rewriting header in the `common` section, or in the request method's own section | refused |
| A name padded with a non-breaking space, which axios sends trimmed | refused |
| An array value | refused |
| A header in another method's section | not refused, and axios drops it |
| A `null` or `false` value | not refused, and axios does not send it |
| A CRLF inside a value | not refused, and no second header reaches the wire (checked on a loopback server) |
| A name with invalid characters (a colon, a zero-width space) | not refused, and Node refuses to send it (`ERR_INVALID_HTTP_TOKEN`) |

- Nothing adds a caller-chosen header after the interceptor, except through request options.
- Neither package names a refused header or any of the residual routing headers: 265 files of stream-chat and 89 of axios. So no chat case is refused falsely.

**`configure --apply` exits, through `main`.** I ran every combination of signal, what replaced its stop, and how the record write ended, for both commands, with the test fakes:

| Situation | Exit |
|---|---|
| A 402, or a 429 with code 9, whatever replaced the stop | 3, with 0 requests after the signal |
| The same, when a Ctrl-C replaced the stop | the Ctrl-C reaches `main` |
| A Ctrl-C during the record write, after a signal | 3 |
| No signal, a refused step or no failure, write succeeding or failing | identical to `438d047` |

The only exit that changed from `438d047` is a signal with a failed write: 3, where it used to be an uncaught `OSError`. The ledger's signals are kept in memory only: `UsageLedger.load` restores the session counts, not the signals.

##### The manager's dispositions

I agree with all of them.

- **C5 verified and integrated:** agree.
- **Deviations accepted** (the trim, the underscore spelling, a method that is not a name, the ledger deciding what reaches `main`, the reminder methods' own rule, nit 5's two variants, nit 4's line): agree. Each only narrows what may be sent or validated.
- **A Ctrl-C during the record write after a signal exits 3, with the Ctrl-C chained:** sound. Nothing more is sent, the Ctrl-C is not lost, and exit 3 carries the more important fact to the operator.
- **No allowlist of header names in the runner, for P06.1:** agree. A caller's header can be set only through request options. No matrix step can now pass them, and none of the roughly 35 harness `call` sites does; I checked each one. I would reconsider it before the harness is used live again in P06.2.
- **No argument counts enforced by the runner at run time, for P06.1:** agree, for the same reason. The harness's own `call` ops also use methods outside the allowlist (`markRead`, `getUnreadCount`, `castPollVote`, `unbanUser`, `show`, `pin`, `archive`, `acceptInvite`, `rejectInvite`). I checked each one: none takes request options or builds an unencoded path.
- **The two pre-existing items, recorded and not fixed:** agree. `unittest discover` still finds the test classes defined after the main guard, and `cmd_run`'s final write sends nothing more.

##### Areas with no findings

- The header-name reading, and the residual routing and non-header options: unreachable by every matrix step and harness op, as recorded (except finding 1's rewording).
- The tests: each tests what it claims, and each would fail if its fix were broken another way. For example, the header refusal fails if it were moved after the budget or limited to product paths, because the chat-path cases would then read `budget`.
- The reversal table.
- The evidence record: byte-identical to `438d047` apart from the marked line 3600 and the appended section. Every one of the 34 `file:line` citations I checked in C5's section is correct, and so are the counts (39 pairs; 10, 5, 1 and 8 tests; 265 and 89 files). The manager's section at `8cac8d0` only appends.
- The README's rules and limits match the code, apart from finding 1.
- Scope: only the 9 paths, all mode 100644, no symlink, and no dependency file, lock, `.npmrc`, `pyproject.toml`, baseline or workflow changed since `c83bedf`.

##### Checks run

| Check | Result |
|---|---|
| `git diff --check 438d047… HEAD` | no output, exit 0 |
| Installs, in a scratch export, `env -i`, proxy and CA variables by reference | `pip install --require-hashes` OK; `pip check`: "No broken requirements found."; `npm ci --ignore-scripts`: "found 0 vulnerabilities"; stream-chat 9.53.0, axios 1.20.0 |
| Unit tests | `Ran 570 tests`, `OK` |
| Ruff check / format / mypy | "All checks passed!" / "55 files already formatted" / "Success: no issues found in 53 source files" |
| `node --check` on the four `.cjs` files | OK |
| `checks/run_plan.py`, no `.work` | "run plan: fits", exit 0 |
| `checks/fix_reversals.py`, 01:31:14–02:00:14 UTC | "reversals: 391, not demonstrated: 0", exit 0. 505 assertion failures, 50 errors, 3 test processes stopped by Ctrl-C by design; no syntax, import or name error |
| The 13 C5 reversal entries | each fails for the reason C5 recorded (for example `'budget' != 'refused'`, `['unset', 5, 21] != [0, 0, 0]`, `OSError(…) != 3`, `TypeError: unhashable type: 'list'`). "C4 re-check 1" fails only its Ctrl-C test, `KeyboardInterrupt not raised` |
| Secret scan of the whole diff (119,481 bytes) | 0 JWT-shaped strings, email addresses, private keys, AWS, GitHub or Slack tokens, bearer tokens or secret assignments. The only 40-hex string is a commit SHA |
| CI push run 371 ([36360951436](https://github.com/amthorn78/glow-dating-app/actions/runs/36360951436)) on `11b5771` | 7 of 7 jobs success; "Stream proof checks" ran every step, not skipped |
| CI PR27 pull-request run 374 ([36365364988](https://github.com/amthorn78/glow-dating-app/actions/runs/36365364988)) on `8cac8d0` | 7 of 7 jobs success; "Stream proof checks" ran every step; the gate passed |

My own offline experiments, all in scratch copies:
- the header probes against the real runner;
- the axios and Node wire check, on a loopback server only;
- the nested-JSON probe;
- the `configure` exit table through `main`, at the head and at `438d047`;
- the clause-removal experiment (finding 2);
- the exception-chain probe (finding 3);
- the SDK method scans.

##### Limits

- Nothing was run live. Whether Stream or its edge honours the rewriting or routing headers, or decodes nested JSON, is not known.
- The API key was absent, so the secret scan could not search for its value.
- The safety of axios's `maxRedirects: 0` rests on the axios source and on the unit test of the interceptor. No redirect was exercised.
- I did not read ADR 0003 (nit 3) or other governing Markdown; both are out of scope.

I changed nothing in the repository, on GitHub or in Notion. `git status` is clean at `1a5f58a`, and all scratch work stayed in the session's scratch directory.

#### Manager verification of the review (App Manager 5, 28 September 2026)

The session committed nothing, so there is no branch to check. The manager checked the report's claims against the reviewed head `1a5f58a`, in the scratch export it verified C5 in (the head's harness, with stream-chat 9.53.0 and axios 1.20.0 installed). It made no Stream call.

- **Identity and classification.** The prompt revision, the head, the merge base, the ancestor check and the diff's size are what the prompt expects. The second and third classifications' results and path counts (18 and 5) match the manager's own runs. One slip, with no effect: the first classification lists 147 paths, not 145, in the manager's run of the same policy on the same SHAs (GitHub counts 148 at `8cac8d0`, which adds this review's prompt). Its result, full scope, is the same.
- **Nit 1, confirmed:**
  - the runner's check parses a query or `params` value's JSON one level deep (`client/runner.cjs:234`–`243`), and `deniedField` (`client/product-op.cjs:53`) reads no JSON inside a string. With the real `productRefusal` and the runner's one-level parse, `{"payload": "{\"ring\": true}"}` is refused ("denied field (ring)"), and the two-level form is not;
  - `validate`'s mirror, `products.client_refusal`, reads no JSON inside a value at all: it passes both forms and refuses a plain `ring` key. So a `product` step's `params` can carry the two-level form past `validate` and the runner. A matrix `get` of a Video or Feeds path is refused by `validate` (C4's rule, `matrix.py:2144`), so for a matrix step the route is the `product` op's `params`;
  - the wording dates from C4. At `438d047` the README already listed nested JSON among the "request options a `call` of a client URL method could pass". C5 kept it under "reachable only through a request-options argument" (`README.md:398`), and its section says the same (`:4191`) and quotes the README (`:4107`). C4's section at `:3600` names only the `proxy`, `socketPath` and adapter residuals;
  - not in a class, as the review says: the residual is C4's, the C4 review assessed it, no case or harness op carries one, and whether Stream decodes JSON nested inside a JSON query value is not known.
- **Nit 2, confirmed.** `_Applied.stop` (`cli.py:157`–`160`) returns the re-read's failure when it is a `GuardrailStop` or not an `Exception`.
  - With the `isinstance(later, GuardrailStop)` clause removed in the manager's scratch export, all 570 tests still pass; the file was then restored and compared with the head.
  - The budget check (`usage.py:126`–`135`) raises a `GuardrailStop` without recording a signal. So after C5 the clause matters only for a budget stop in the re-read after a refused step: with it the stop reaches `main` (exit 3), and without it `finish` returns 1.
  - The budget refuses before sending, so nothing is sent either way.
- **Nit 3, confirmed.** At `438d047`, `finish()` raised `self.failure` itself. At the head, it raises the stop from `ended_on()` whenever the two differ (`cli.py:176`–`181`).
  - Without a signal, an ordinary error as the failure lets the re-read run (`may_read_after`). If the re-read fails too, the apply's failure is raised from the later re-read error, and loses its own cause.
  - The exit code is unchanged, and so is the record, which keeps both failures.
- **The review's other claims match the manager's own checks at the head:**
  - 570 tests, and the lint, format and type checks;
  - 391 reversals, none "not demonstrated", with 505, 50 and 3, and each C5 entry's failure reason;
  - the 132 cases passing `validate`, the 39 pairs, and the 265 and 89 package files;
  - the record byte-identical to `438d047` outside line 3600 and C5's section;
  - push run 371 and PR run 374.
- **Spot checks of the harness's own `call` methods outside the allowlist,** in stream-chat 9.53.0: `castPollVote` encodes both path values; `unbanUser` and `getUnreadCount` pass their values as query parameters; `acceptInvite` and `rejectInvite` send theirs in the body.
- **Not re-run by the manager:** the session's header probes, its loopback wire check, its exit table through `main` and its SDK scans.

#### Disposition

- **Approve: C5 stands, and P06.1's harness code stands as reviewed.** Its fixes are confirmed, no finding falls in a class that needs another correction pass, and no recorded result changes. The economics discovery is next. The Dev Manager reads its prompt first (DM-06), because the session acts in Nathan's signed-in Stream dashboard.
- **Nit 1 is corrected in the records by the manager, in this batch.** The corrections are at `README.md:398` and in this record at `:3600`, `:4107` and `:4191`, each marked with App Manager 5 and the C5 review's nit 1.
  - They record that JSON nested two levels deep can reach the runner through a `product` step's `params`, and that the runner reads one level of JSON while `validate` reads none.
  - No code changes. The manager's own miss is AM5-06: its verification of C5 found "no slip" in C5's section.
- **Nits 2 and 3 are recorded, not fixed in P06.1.** Neither sends a request or changes a recorded result, and P06.1 has no further harness session. They go to the harness's next use, with the review's advice to reconsider an allowlist of header names before the harness is used live again (P06.2, if it reuses the harness):
  - **nit 2:** a test in which the re-read after a refused step meets a budget stop that must reach `main`, and a reversal that removes only the `isinstance(later, GuardrailStop)` clause;
  - **nit 3:** `finish()` chains only a signal's stop to what replaced it, so an apply failure keeps its own cause.
- **The manager's dispositions of C5 stand;** the review agrees with each.
- **Nathan's pick for this review: Opus 5.5 at extra high,** recorded in the uses table.

## Economics discovery (28 September 2026)

Nathan ran the read-only discovery in Claude in Chrome, in his own browser signed in to the Stream dashboard, from revision 2 of the [economics discovery prompt](../../ephemeral/2026-09-28-p06-1-economics-discovery-prompt.md), written at `78a0a45`. Revision 2 applies the Dev Manager's DM-06 conditions, so it needed no further read. Nathan relayed the session's notes and report to App Manager 5 on 28 September; the model and level he ran it on were not stated. The session used no API key or secret and, as its report says, changed nothing: navigation and reading only, with the interactions it lists. It finished reading at about 20:37 UTC.

- **The account** (dashboard; account-specific):
  - the plans are Free Chat, Free Feeds and Video Build, $0 for 1 to 30 September, not a trial;
  - no payment method is on file, and no spending cap or usage alert is shown;
  - the eight Chat limits are unchanged since 25 September;
  - Chat, Video, Feeds and Moderation are in US East;
  - the "DEV" badge carries no explanation, and no Maker status is shown.
- **September's usage:**
  - Chat, 1 to 28 September: 2,262 API calls, 152 QueryChannels calls, a peak of 5 concurrent connections and 5 MB outbound;
  - Feeds, in a chart that covers 24 to 28 September only: 9 activities, 2 follows and 171 API requests;
  - Video: none.
  - No warning is shown, and nothing is near a limit.
- **Stream's public pricing and terms** (general policy, paraphrased by the session with each page named):
  - Chat's plans are Build (free), Start ($399 a month billed annually, $499 monthly), Elevate ($599 and $675) and Enterprise; the Fair Usage document's overage rates apply to every plan.
  - The Maker program, if approved, gives 2,000 monthly active users and 100 concurrent connections with hard limits, for teams of fewer than 5 with under $100k funding and under $10k monthly revenue.
  - No page says what a free Chat account does at a limit; the terms (section 4.6) let Stream suspend or limit usage above plan limits without payment.
  - No attribution is required (terms, section 3). No page read excludes any kind of app, and no clause names dating or adult content.
  - The data-processing addendum is a self-serve PDF, not opened; the privacy statement names the EU–US Data Privacy Framework and standard contractual clauses. No public list of Chat hosting regions was found.

### The report, as relayed

The session's notes before its report, as relayed, verbatim; the line breaks between notes are restored:

> Started: I'm in the Stream dashboard in a new tab (read-only). The app list shows "Glow Connection System Chat Engine" (ID 1729640, DEV badge, US East). Next I'm opening Billing and Usage pages.
>
> Progress: Billing and Chat usage pages read (plan "Free Chat", limits unchanged, no payment method shown). Video/Feeds usage default to Sep 24–28, so I'm opening the date-range picker (view-only) to get Sep 1 onward.
>
> Progress: Feeds/Video usage read. On the app list I'm now hovering the DEV badge (no clicks) to see whether the dashboard explains the mode limits; then I'll check for Maker/compliance notices.
>
> Progress: Part A (dashboard) is read. Now on getstream.io: Chat pricing page read (Build free / Start $399 / Elevate $599 / Enterprise). Next: Fair Usage doc, Video & Feeds pricing, Maker page, legal/terms.
>
> Progress: Terms of Service (last updated October 2024), Maker pages, Video/Feeds pricing and the Fair Usage doc are read. Now reading the Data Processing Addendum and subprocessors pages, then I'll check for an acceptable-use policy, regions, and the free-plan-at-limit behaviour.
>
> Progress: DPA page (effective 26 Feb 2024, PDF download only — I won't download it), subprocessors page (last update September 2026), privacy statement (DPF + SCCs) and security page read. Now looking for hosting regions and message-retention docs on getstream.io.
>
> The docs search box is open (a search box on getstream.io, which is permitted). Typing a query there.
>
> Progress: Data-retention doc read (hard-deletes, optional policy 24h–5 years). I can't find a public list of Chat hosting regions in the docs yet; trying the Trust Center (a getstream.io subdomain, read-only, no forms), then one check for an acceptable-use policy and free-plan-at-limit wording.
>
> Progress: Trust Center page rendered blank in the browser (and read tools errored), so I'm treating it as not readable. Checking one candidate acceptable-use policy URL on getstream.io now.

The report, as relayed, verbatim:

> Stream (getstream.io) lookup for Glow: report on prompt revision 2
> Quoting: my rules cap me at one short quote per response, so I paraphrased policy wording and gave the page where the exact text sits. Names, numbers and labels are reported as shown. The one quote is under item 12.
> Prompt revision received: revision 2 (App Manager 5, 28 September 2026).
> Checked at: 2026-09-28 20:37 UTC (approximate; taken when I finished reading).
> Sites opened:
>
> * dashboard.getstream.io
> * getstream.io, including its docs pages
> * trust.getstream.io, which rendered blank and could not be read
>
> I did not open the DPA PDF, which is hosted on amazonaws.com. I only recorded its link.
> A. Dashboard
>
> 1. Plan: The plans are Free Chat, Free Feeds and Video Build (billing page). No trial is shown. The billing period is Sep 1 – Sep 30, and the amount for it is $0.00 (billing page). Confirmed; account-specific.
> 2. Limits: All eight limits match 25 September (Chat usage page, Metrics & limits table):
>    * 1,000 active users
>    * 100 concurrent connections
>    * 2,000,000 API calls
>    * 200,000 QueryChannels calls
>    * 500,000 stored channels
>    * 5,000,000 stored messages
>    * 5,500,000 total records
>    * 500 GB outbound traffic
>    * Billing page, Free Chat: 100 concurrent connections included, and an outbound bandwidth allowance shown as "512,000 units" against a usage of "5 MB". The units are unclear.
>    * Billing page, Free Feeds: 5,000 activities and 200,000 API calls included.
>    * No Video limit is shown. Confirmed; account-specific.
> 3. Usage:
>    * Chat (Sep 1–28):
>       * API calls 2,262
>       * QueryChannels 152
>       * Concurrent connections 5
>       * Outbound traffic 5 MB
>       * Active users, stored channels, stored messages and total records show "—" (not shown)
>    * Feeds (charts cover Sep 24–28 only):
>       * Activities 9
>       * Follows 2
>       * Peak concurrent connections 5
>       * API requests 171
>    * Video: the page says no usage in the period.
>    * Range: the Sep 1–30 period isn't over. Video and Feeds charts wouldn't widen past Sep 24–28, so the billing page's Sep totals are the wider view.
>    * Warnings and limits: no warnings are shown, and no usage is near a limit. The highest is 5 of 100 concurrent connections. No new billing period has begun. Confirmed; account-specific.
> 4. Past a limit:
>    * The dashboard gives no statement of what happens. It offers only a "Fair Usage" link and a "Contact Sales" button (Chat usage page). I clicked neither.
>    * Payment method on file: No. The billing page's Payment Method section reports no Stripe ID assigned.
>    * Spending cap or usage alert: not shown.
>    * Invoices: none found. Not shown; account-specific.
> 5. Maker: not shown on any allowed dashboard page (apps list, billing, usage). Not shown.
> 6. Region and mode:
>    * Chat, Video, Feeds and Moderation for app 1729640 all show "US East" in the app list.
>    * The DEV badge has no tooltip and no explanation of limits or of what production requires.
>    * Nothing is shown about other regions or changing region.
>    * The Stream docs (general) say a Stream app can be in development or production mode, that you can switch later, and that production mode disables certain destructive dashboard features. That is the docs, not the dashboard. Confirmed for region; not shown for the rest.
> 7. Attribution and agreements: no branding or attribution notice, DPA, or security or compliance document is offered on the pages I was allowed to open. The account menu has only Account and Logout, and I did not open Account. Not shown.
>
> B. Public site
>
> 8. Chat pricing (getstream.io/chat/pricing/; no "last updated" date shown):
>    * Build (free): 1,000 MAU and 100 concurrent connections. The feature table says total API calls up to 1M, Query Channel calls up to 100K, and API bandwidth up to 10 GB. That is lower than your dashboard limits (item 2).
>    * Start: $399/mo billed annually or $499 monthly, with 10,000 MAU and 500 concurrent connections.
>    * Elevate: $599/mo billed annually or $675 monthly, with 10,000 MAU and 500 concurrent connections.
>    * Enterprise: contact sales.
>    * Overage on the pricing page: the MAU and concurrent overage rows read "Limits Apply", with no rates.
>    * Overage rates in the Fair Usage doc (getstream.io/chat/docs/node/fair-usage-limits/, no date; it applies to every Chat plan): stored messages $5.00 per 1M, stored channels $100.00 per 1M, outbound traffic $0.40 per GB, API calls $7 per million, query-channel calls $2.50 per 100,000. Your dashboard limits match its lowest band ($0–$6K annual spend).
>    * Free plan for commercial production: not stated on the pricing page. No excluded app types are named (dating and adult are not mentioned). Confirmed for prices; not shown for commercial use; general policy.
> 9. Video and Feeds: both are priced separately from Chat.
>    * Video: free Build plan with 333,000 participant minutes (page also says "$100 in free credits"). Pay-as-you-go is $0.30 per 1,000 participant minutes. Add-ons are priced per 1,000 call minutes.
>    * Feeds: free plan with 125,000 API calls and 5,000 activities; overage is listed as "Not allowed". Start is $499/mo billed annually ($599 monthly). Elevate is $899/mo billed annually ($999 monthly). Your dashboard shows 200,000 Feeds API calls included, which differs from the public 125,000.
>    * Confirmed; general policy.
> 10. Free plan past a limit with no payment method:
>    * No page states this directly for Chat.
>    * The Fair Usage doc says usage above thresholds is billed as overage.
>    * Terms section 4.6 lets Stream suspend or limit usage above plan limits without payment.
>    * Feeds free plan overage is listed as "Not allowed".
>    * Unclear; general policy.
> 11. Maker Account (getstream.io/maker-account/ and getstream.io/blog/maker-account/):
>    * Eligibility: under 5 team members (the blog says "fewer than 5"; the program page says "five or less"), under $100k funding, and under $10k monthly revenue. Availability is limited.
>    * Includes: a modified Chat Start plan (2,000 MAU, 100 concurrent connections), the Feeds Start plan (125,000 API calls a month), Video Build (333,000 participant minutes), AI Moderation pay-as-you-go with a $100 monthly credit, and hard limits. Support is low-priority.
>    * Duration: the blog says free indefinitely while you qualify. Applying starts a 30-day free trial that converts on approval.
>    * When it ends: terms section 4.5 says you keep Maker status only while qualifying. If you exceed the criteria without upgrading, Stream may disable access without notice. Volume above the cap is rejected until the monthly reset or an upgrade.
>    * Commercial production and excluded apps: the blog FAQ says regular terms apply and you can build anything. No excluded app kinds are named.
>    * Attribution or publicity: none stated on the Maker pages.
>    * Confirmed; general policy.
> 12. Attribution: none required. Terms section 3 says "Customer's implementation of the Service will not require displaying Marks to End Users" (getstream.io/legal/). The same section says not to remove Stream marks from the Service or its code files. Looked at:
>    * the three pricing pages
>    * both Maker pages
>    * the terms
>    * Confirmed none found; general policy.
> 13. Data processing and region:
>    * DPA: getstream.io/legal/dpa/, effective Feb 26, 2024. It is a self-serve PDF download with no request form seen. I did not download it, so the transfer mechanism it names is unverified.
>    * Transfer mechanism: the privacy statement (getstream.io/legal/privacy/, effective Feb 27, 2024) says Stream is certified under the EU–US Data Privacy Framework, with the UK Extension and the Swiss–US framework. It also says EU Standard Contractual Clauses are used with recipients in countries without adequate protection.
>    * Retention: the Chat pricing FAQ says messages are stored as long as the plan is active. The docs offer an optional retention policy of 24 hours to 5 years, and deletion is a permanent hard delete. The security page (effective June 2025) says data can be deleted via API or by requesting deletion from Stream's privacy contact. How long deleted data survives in backups is not shown.
>    * Hosting regions for Chat: no public list found. The app-settings doc says you can control the primary region, where data is stored. The security page mentions dedicated regional servers as an Enterprise option.
>    * Changing region after creation: unclear.
>    * Subprocessors: getstream.io/legal/subprocessors/, last update September 2026.
>    * Mixed; general policy.
> 14. Terms: https://getstream.io/legal/, last update October 2024.
>    * Price change notice: at least 30 days' advance notice, and increases take effect at the next renewal term (section 4.2).
>    * Acceptable-use policy: none found. The Legal Center links don't list one, and one guessed URL returned 404.
>    * Dating or adult content: no clause names either.
>    * Content-moderation duty: section 6.2 requires you to limit End User access to people who agree to your own terms. It also requires commercially reasonable efforts to detect, address and remove content that violates your terms.
>    * Confirmed; general policy.
>
> Changes since 25 September
>
> * Item 2 limits: no change.
> * Usage has changed from 10 API calls and everything else zero. It now shows:
>    * Chat: 2,262 API calls, 152 QueryChannels calls, 5 concurrent connections and 5 MB outbound
>    * Feeds: 9 activities, 2 follows, 171 API requests
>    * Video: none
>
> Risks noticed
>
> * No payment method is on file, and no page says what a free Chat account does at a limit.
> * The Maker hard cap and the terms 4.5 disable-without-notice clause apply if you go that route. Chat under Maker is 2,000 MAU and 100 concurrent connections. The $10k monthly revenue and $100k funding caps also apply.
> * Public Build-plan figures (1M API calls, 100K QueryChannels, 10 GB bandwidth, 125,000 Feeds calls) are lower than what your dashboard shows.
> * No attribution requirement and no excluded app kinds were found in the pages I read. I could not read the DPA PDF or the Trust Center, so those two sources are unchecked.
> * Nothing is near a limit. The app is on DEV, US East.
> * Terms section 12.5 lets Stream use your name and logo in client lists and marketing.
>
> Actions taken: navigation and reading only, plus these interactions:
>
> * I opened the Video/Feeds date-range picker (no change made).
> * I opened the account dropdown without clicking Account or Logout. It showed your email, which I did not record.
> * I typed only into the docs search box on getstream.io. Two typing actions ran while that box wasn't focused, so that text went nowhere.
>
> No secrets were visible. I opened no app-level pages. I opened no Edit, Configure, Contact Sales or Register controls. Nothing was downloaded, and I clicked nothing that changes a plan. The tab I created is closed, and your original tab was left untouched.
> The report is this message; I did not save it to a file.

### Manager verification (App Manager 5, 28 September 2026)

- **What the manager could check.** The manager opened neither the dashboard nor Stream's public site: its rules forbid connecting to a provider, as the Dev Manager's did for DM-06. So the dashboard facts rest on the session's report, as the baseline's did, and the public facts rest on its reading of the pages it names. The manager checked the report against the prompt's rules, the brief's baseline and this record's usage ledgers.
- **Against the prompt's rules:**
  - it received revision 2;
  - **sites:** it opened dashboard.getstream.io, getstream.io and trust.getstream.io, a getstream.io address the rules allow. It recorded the data-processing addendum's link on amazonaws.com without opening it;
  - **dashboard pages:** the application list, billing and usage, all in the allowed set; no application page;
  - **clicks:** the Video and Feeds date-range picker, with no change; the account menu, a menu, which showed Nathan's email, not recorded. A hover over the "DEV" badge is not a click;
  - **typing:** only in the docs search box on getstream.io, as allowed, except that two typing actions ran while the box was not focused. The session says the text went nowhere, and nothing was submitted. **A deviation, disclosed;**
  - nothing was downloaded, recorded or submitted, and no plan, trial, checkout, program, agreement, booking or contact control was used. No secret was visible, and the session's own tab was closed;
  - **quotes:** the rules ask for the exact words about charges, overage, limits, attribution, eligibility and data processing. The session gave one quote (item 12) and paraphrased the rest, naming each page, because its own rules allow one short quote per response. **A deviation, disclosed;** see the disposition.
- **Against the baseline of 25 September** (the brief): the plan, the billing period, the $0, the missing payment method, US East, the "DEV" badge and all eight limits match. New: the billing page names Free Feeds and Video Build too. The Free Chat outbound allowance, "512,000 units", is 500 × 1,024, so it is plausibly 500 GB in megabytes; that is the manager's arithmetic, not a dashboard statement.
- **Usage against the sessions' ledgers** (DM-06 finding 5 (d)). The four sessions that called Stream counted 2,261 API calls between them, for every product, server and client: I1 884, the I1 review 119, I2a 698 and I2b 560 (this record's usage sections). The baseline showed 10 calls before I1.
  - I2b sent its Video and Feeds requests to the chat host, as the server SDK does. If the dashboard's Chat count includes them, the sessions account for 2,252 of its 2,262 calls, and the ledgers counted 9 more than Stream did.
  - If the Chat count excludes them, the Feeds page's 171 requests come on top, and Stream counted up to 162 more than the ledgers, about 7%. The ledgers do not split calls by product, so the exact figure is not known.
  - **Either way the difference is small.** The ledger enforced the budget guardrails, and no session came near the 5,000-call cap; September's use is about 0.1% of the plan's 2,000,000 calls.
  - The dashboard's peak of 5 concurrent connections is one below I2a's ledger peak of 6. Stream samples connections; the ledger counts every connection the harness held at once.
  - **Feeds:** the 2 follows match I2b's records: the client's follow in the V1 rerun and the server's replay in run V2. The 9 activities are consistent with the three V runs' adds, which the records do not count.
  - **Stored data:** the dashboard shows "—" for active users, stored channels, stored messages and total records, so it cannot be compared with the cleanups' "nothing remaining". I2b's last `verify-clean` (27 September, 06:30 UTC) found no proof user, channel, call, feed or activity.
- **Inside the report:**
  - The public Build plan's figures (1M API calls, 100K QueryChannels calls, 10 GB bandwidth) are below this account's limits, which match the Fair Usage document's lowest band. The public Feeds allowance (125,000 API calls) is below the dashboard's 200,000.
  - The dashboard's figures are this account's; which figures bind a production application is not stated.

### Disposition

- **The discovery is recorded, and it answers the economics outcome (the brief's outcome 5) as far as a read-only look can:**
  - **the plan's real limits:** the eight Chat limits on the dashboard, with the Feeds allowances and no Video limit;
  - **the costs that would apply:** Stream's public plans and the Fair Usage overage rates;
  - **the usage the proof caused:** the September figures above, within about 7% of the sessions' ledgers (at most 162 calls, 7.2% of the ledgers; this line said "within 7%" until DM-07 item 5 corrected it);
  - **the approvals P06.2 needs:** none. P06.2 works on the same development application, and the proof's use was about 0.1% of the plan;
  - **the approvals launch needs:** a billing decision before any real traffic, as the brief already says (A04). The free plan allows 1,000 monthly active users and 100 concurrent connections; the Maker program, if approved, 2,000 and 100 with hard limits while Glow qualifies; Stream's Start plan costs $399 a month billed annually, for 10,000 monthly active users. No payment method is on file, and the budget is $0 (OD-12).
- **The deviations are accepted:**
  - **Paraphrase instead of exact words:** a limit of the tool, disclosed. Before any decision rests on Stream's exact wording (the overage and suspension terms, the Maker criteria, the data-processing addendum), that page is read then; the report names each page. A later prompt of this kind asks for the page and a close paraphrase, with at most one quote.
  - **The account menu:** within the rules on menus; no personal data was recorded.
  - **The two unfocused typing actions:** no text reached a form, and nothing was submitted. A later prompt asks the session to type only once the search box has focus.
- **DM-06 finding 5 (e): nothing to put to Nathan.** The pages read show no attribution requirement (terms, section 3), no excluded kind of app and no restriction on production use. The data-processing addendum's PDF and the Trust Center were not read, so those two sources are unchecked.
- **Two terms bear on later phases.** They are recorded here, not decided:
  - **Section 6.2:** the customer limits End User access to people who agree to its own terms, and makes commercially reasonable efforts to detect, address and remove content that breaks them. This is for P07's moderation plan (A05).
  - **Section 12.5:** Stream may show the customer's name and logo in its client lists and marketing. Outside the app, this bears on Nathan's principle that nothing should indicate anything outside Glow (A04).
  - The close-out consultation asks the Dev Manager whether either is Nathan's to decide now (OD-32). DM-07: neither is; see the next section.
- **Where the facts live:** this section and the brief's "Sessions", with Notion's A04 and A05 rows. PF01 is not changed: it changes only when a rule does (DM-01 P3), and no rule changed. R04 is unchanged: its cost trigger, a price above the approved budget, is the launch decision A04 already records.
- **Maker:** the dashboard shows no status, so OD-22's "pending" stands.
- **Nathan's pick** for this session was not stated; the uses table keeps "pending".

## The Dev Manager's close-out read (DM-07, 29 September 2026)

Dev Manager 2 read the manager branch at `89a8d01` ([report](../../continuity/dev-manager/reviews/2026-09-29-dm-07-p06-1-close-out-read.md); the manager's disposition is in the [review log](../../continuity/dev-manager/README.md), "DM-07"). What bears on this record:

- **The live read (item 4 (a)): none in P06.1.** No recorded verdict rests on the other roles or settings, and every lockdown body named only client roles. **Condition for P06.2:** the harness's first live use in P06.2 runs `products.verify`, the full comparison P06.1-C4 added, before any other live command. Its result closes ADR 0003 condition (c) and the architecture document's section 5 caveat, or stops P06.2 if it differs. This settles what the I2b review's disposition left to the close-out.
- **The activities query and the resource roles (item 4 (b)): left open and recorded.** The design constraint closes both paths: the server creates no call, feed or activity for a user, and the harness preflight refuses unowned ones in a proof run. Before the production application is configured (P09 or P11), Nathan decides whether production relies on that constraint alone, or also closes the paths in configuration: emptying `call_member` and the feed-creator grants, or disabling Video and Feeds if Stream allows it. The P06.2 brief carries the question in OD-32's form. It is not his now.
- **The economics disposition (item 5): approved.**
  - 5 (d) confirmed, with the wording "within about 7%": if the Chat count excludes I2b's Video and Feeds requests, Stream counted up to 162 more calls than the ledgers, 7.2% of the ledgers or 6.7% of Stream's total; either way the difference is immaterial, about 0.1% of the plan. The stored-data comparison could not be made; I2b's last `verify-clean` stands.
  - 5 (e) confirmed: nothing goes to Nathan.
  - **Section 6.2:** not Nathan's now; it belongs to P07 (A05). Before the P07 brief relies on it, the clause is read in Stream's exact words.
  - **Section 12.5:** not Nathan's now; it belongs to A04, the billing and launch decision, where it goes to him in OD-32's form if it survives an exact reading. Before A04, the exact text is read, including whether it allows opting out by written notice; if it does, the A04 item gives Nathan that option.
  - PF01 left unchanged: agreed.
  - **The paraphrase** is enough to record the facts, not to decide on them. Before a decision rests on Stream's exact words, that page is read again: terms 4.5, 4.6, 6.2 and 12.5, the Fair Usage rates, the Maker criteria and the data-processing addendum. For A05, the addendum's PDF and the Trust Center are unread, so the transfer mechanism and the hosting regions stay "unverified" until a later read, under a Dev Manager-approved prompt if it acts in Nathan's signed-in browser.
  - The account menu and the two unfocused typing actions: accepted as disclosed.
- **Nathan's close-out items (item 6):**
  - (a) the development application's lockdown stays for P06.2: Nathan's decision; both managers recommend it;
  - (b) the development secret is replaced as OD-28 directs, as soon as Nathan can; nothing needs it until P06.2's first live session;
  - (c) answered by Nathan on 29 September (OD-36): two environments, assigned per session.
- **Nathan's answer on (a) and (b)** (29 September, OD-37): *"Stop worrying so much about this secret. I want to move forward with dev"*. The development application stays locked down for P06.2, the recommended option, which needs no action; the secret's replacement is no longer a close-out item.

## P06.1 merge receipt (App Manager 5, 29 September 2026)

- **Close-out:** Nathan's answer to the close-out message (OD-37): *"Stop worrying so much about this secret. I want to move forward with dev"*. The development application stays locked down for P06.2; the development secret's replacement is no longer a close-out item.
- **The final head:** `c57de50f6ae2cb9effa6226d82c3ef646a51ac0f`. Every commit after C5's reviewed code head `11b5771` is Markdown-only (the trusted classifier on `11b5771..c57de50`: ordinary documentation only), and no governing file changed after `c775f39`, the commit that applied DM-07's conditions.
- **CI on the final head:** [PR run 36510118431](https://github.com/amthorn78/glow-dating-app/actions/runs/36510118431) ran all seven jobs, "Stream proof checks" included, and passed; the rendered suite passed, and the gate log says `Application checks passed`. Push run 36510114608, Markdown-only against `c775f39`, skipped the application jobs by design, and its gate passed.
- **Codex:** App Manager 5 marked PR27 ready at about 01:55 UTC. Codex's code review completed at 01:57 UTC and its security review at 02:03 UTC, both on `c57de50`, with no findings: no review or comment, and its "no findings" reaction on the PR.
- **Merge:** a merge commit at about 02:07 UTC, with the expected head pinned to `c57de50`. The merge commit is `47db18dfec3f62626f4e09f65f52c7a2e10c9e3e`, with parents `0f45e648099b415217938c25d7369164c0101def` and `c57de50f6ae2cb9effa6226d82c3ef646a51ac0f`. Its tree, `d5d4bbe486559897305b70cfcc2f9af510286c91`, is the final head's tree.
- **After the merge:** the manager branch `claude/magical-wozniak-yfmmx2` restarts from `main` for the next item, P06.DB (OD-17). The P06.1 prompts in `docs/ephemeral/` stay until a later records batch replaces their links with commit-pinned ones and prunes them; Git history keeps their text either way.
