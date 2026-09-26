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
| 5. Replies matched to commands | Fixed | `glow_stream_proof/client_bridge.py:202` (id check), `:142` reader thread, `:183`, `:192`; a timeout, mismatch, non-JSON line or exit ends the session (`:156`), and its later commands raise `ClientSessionEnded` without being sent; `proof_run.py:930` records affected cases INCONCLUSIVE | `tests/test_client_session.py` (fake runner scripts: mismatch, timeout, two replies in one write, exit) |
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
| 13. Client-created polls and groups not cleaned up or listed | Fixed: tracked and deleted; verify-clean lists polls and user groups, counting only those absent at preflight | `proof_run.py:1161`, `:2417`, `:2345` | `tests/test_cleanup.py` `ClientCreatedDataTest`, `PreexistingPollsAndGroupsTest`; `tests/test_cli.py` `test_verify_clean_lists_polls_and_user_groups` |
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
