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
- **A run's results were lost.** In run `p061i1-0925031802` an exception escaped before the results were written. The harness then wrote a progress file after every case, and the results after any `Exception`, but not after Ctrl-C (`KeyboardInterrupt`), which escaped before they were written (corrected in P06.1-C1; since P06.1-C1 Ctrl-C is handled too).
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
