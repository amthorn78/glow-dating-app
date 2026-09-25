# P06.1-I1 implementation prompt — Stream sandbox harness and bypass matrix

- **Owner:** App Manager 3. Nathan starts this session manually and relays its report.
- **Durable brief:** [P06.1 brief](../planning/p06-1-chat-provider-proof.md). Evidence: `docs/testing/evidence/2026-09-25-p06-1-chat-provider-proof.md`, which this session creates.
- **Recommended reasoning level:** extra high. The manager and TypeSafe v4 agree; no ultracode.
- **Deletion condition:** prune after P06.1 closes and the brief and evidence record hold every accepted result.

**Manager:** before giving this prompt to Nathan, replace `<MANAGER_BRANCH>` and `<START_SHA>` with the pushed manager branch and the start commit.

---

You are **implementation session P06.1-I1** for the Glow dating app, private repository `amthorn78/glow-dating-app`. You build and run a sandbox proof of Stream Chat's permission model against Nathan's development Stream application, with synthetic users only.

- Nathan started you manually and will relay your report to the manager (App Manager 3). You are not the manager.
- You may use any tools, subagents, scheduled wake-ups or other capabilities the work needs.
- Your boundaries concern scope: stay within the owned paths, work on your own session branch, and report as below.
- Do not take on manager duties: writing prompts for Nathan, opening or merging PRs, or updating Notion.

## 1. Environment check (names only; never print values)

1. None of `DATABASE_URL`, `HD_API_KEY`, `GEO_API_KEY` may be set: `for n in DATABASE_URL HD_API_KEY GEO_API_KEY; do [ -n "${!n+x}" ] && echo "$n present"; done`. If any is present, stop and report.
2. `STREAM_APP_ID`, `STREAM_API_KEY` and `STREAM_API_SECRET` must be set and non-empty: `for n in STREAM_APP_ID STREAM_API_KEY STREAM_API_SECRET; do [ -n "${!n}" ] && echo "$n set" || echo "$n MISSING"; done`. They belong to Nathan's development Stream application 1729640, and this session uses them. Never print, copy, log or write the secret.
3. Record `command -v node npm npx python3.12` and their versions. Expected: v24.19.0, 11.9.0 and Python 3.12.14, from `$HOME/.local/bin`.
4. Never dump the environment. Never connect to a database, HDE or Railway. Never run `playwright install`, `eas` or `migrate`. The only provider you may call is Stream, and only application 1729640.
5. In a clean process environment, network installs need the proxy and CA variables passed through by reference, never printed; see "Claude Code cloud sessions" in `docs/operations/local-development.md`.

## 2. Start gate

```bash
git fetch origin <MANAGER_BRANCH>
git merge --ff-only <START_SHA>
git rev-parse HEAD   # must print <START_SHA>
```

If the fast-forward or the check fails, stop and report. Then read, completely:

- root `AGENTS.md` and `CLAUDE.md`;
- the P06.1 brief, `docs/planning/p06-1-chat-provider-proof.md`, especially "Stream dashboard baseline" and "Brief — P06.1";
- in `docs/continuity/claude-code-handoff.md`: "Stream Chat setup — current facts and future proof" and "Claude cloud environments";
- in `docs/pf-canon/GAPP-PF01-A-to-Z-Implementation-Plan.md`: section 7's "Chat and notifications" paragraph and section 8's P06;
- `docs/architecture/production-contracts.md` (flows F10, F11 and F13, and the paragraph on send versus revocation), the "P06 and P11 handoff" in `docs/architecture/interactions-fixtures.md`, and PV03 and DB06 in `docs/testing/p11-deferred-acceptance.md`;
- `docs/operations/local-development.md` and `docs/operations/environment-inventory.md`.

## 3. What you are proving

The design (PF01 section 7; contract flows F10, F11 and F13): the server controls channel membership and authorizes every send. A client never sends through Stream directly; the app server sends on the user's behalf after its match and block check. A client's token lets it read its own current match's channel and nothing else.

This session proves the brief's first three outcomes: the checks are enforced, the authorized path works, and no client bypass exists. Revocation, history, outage and economics belong to P06.1-I2; don't start them.

**Treat the application as unsafe until you have checked it.** The dashboard shows "Authentication Checks" and "Permissions Checks" ON, with descriptions of relaxed modes: development tokens accepted, and full permissions for every user. Establish the real settings through the API before any client acts.

Take every Stream behavior from Stream's current official documentation and from what the live application actually does. Don't assume API names, defaults or permission identifiers from memory. Record the documentation pages you rely on.

## 4. Deliverables (owned paths only)

Owned: `proofs/stream-chat/**` (new) and `docs/testing/evidence/2026-09-25-p06-1-chat-provider-proof.md` (new). Everything else is read-only, including `apps/`, `services/`, `packages/`, `scripts/`, `.github/`, the `Dockerfile`, `.dockerignore`, `.gitignore` and the rest of `docs/`. Don't change the fixture API, its configuration or its guards, and set no `GLOW_*` variable.

### 4.1 The harness in `proofs/stream-chat/`

1. **SDKs.** From Stream's current official documentation, choose and pin:
   - a Python server SDK for the harness's server side;
   - Stream's JavaScript client for the client sessions.

   Record each package's name, exact version and the pages you used. Python dependencies go in a hash-pinned lock, installed with `pip install --require-hashes` into an ignored `.venv`. JavaScript dependencies go in `package.json` with exact versions and a `package-lock.json`, installed with `npm ci --ignore-scripts`. Give `package.json` the repository's engines, Node 24.19.0 and npm 11.9.0. Record how you generated the locks.
2. **Credentials.**
   - Only the server side reads `STREAM_APP_ID`, `STREAM_API_KEY` and `STREAM_API_SECRET`, from its own process environment.
   - Never print, log or write the secret or any full token, and don't configure tools that store it, such as a Stream CLI login.
   - Start every client process with an environment that does not contain `STREAM_API_SECRET`: only what it needs, such as `PATH`, `HOME`, the proxy and CA variables, the API key and its own user token.
   - Redact tokens in all output. Evidence may show a token's claims, never the token.
3. **Settings baseline and enforcement.** Before any client acts:
   - read the application's settings through the server API, and record every setting that affects authentication, permissions, guest and anonymous access, and the permission-system version;
   - if authentication checks or permission checks are disabled, enable them, then re-read and record both states;
   - record anything else you change, and how to restore it.
4. **Channel types.** Configure through the server API:
   - A dedicated one-to-one channel type for matches, for example `glow-match`, in which clients may read their own channel but cannot send or change anything. Turn off every feature a client could use to put content in front of the other member.
   - **Every default channel type** (commerce, gaming, livestream, messaging, team) locked so that no client role can create, join, read or send in it. Restrict their grants rather than deleting the types, and record how to restore the defaults.
   - Synthetic users get the ordinary `user` role, never admin or moderator.
5. **The authorized path.**
   - The server issues each synthetic user a token with a short expiry.
   - The server creates the matched pair's channel with exactly its two members.
   - An app-side send function checks the pair's current match and block state in the harness, then sends through the server SDK on the user's behalf. For an unmatched pair it refuses without calling Stream.
   - Both clients read the channel, and each sees the other's server-sent message.
   - Connect, disconnect and reconnect a client over Stream's WebSocket. If the proxy blocks the WebSocket, record the exact failure, run the rest over REST, and mark every realtime case unverified.
6. **The bypass matrix.** Synthetic users: A and B are matched in channel `AB`; X and D are matched in channel `XD`. Every client action below must be refused, and each case needs a positive control (4.2).
   - **Tokens:** a development token; a token signed with a wrong secret; an expired token; A's valid token used for a request that claims to act as B.
   - **Guest and anonymous access with only the API key:** creating a guest user, and connecting anonymously. Neither may reach any channel or user data.
   - **Creating and joining:** A creating a channel of the match type, and of each default type; A adding X to `AB`, adding itself to `XD`, or removing B from `AB`; A changing `AB`'s data, or freezing, truncating or deleting it.
   - **Reading outside its match:** A watching or querying `XD`; querying channels with a filter that names X or D; fetching an `XD` message by its ID; message search across channels; querying other users. Record exactly what, if anything, A can learn about X and D.
   - **Putting content in front of B outside the app's path:** sending a message to `AB`; replying in a thread; editing or deleting the server-sent message; reacting; uploading a file or image; pinning; polls and votes; commands; custom events; and changing A's own user profile fields that B could see.
   - **Self-escalation:** A changing its own role, or any other permission-relevant field.
   - **Realtime:** while connected, A receives events for `AB` and none for `XD`.
   - Typing and read events may stay allowed only if they carry no free text. Record exactly what they can carry.
7. **Usage and guardrails.** Count synthetic users, channels, concurrent connections and API calls per run. Stop before any passes the brief's guardrails: 20 users, 30 channels, 10 connections, 5,000 API calls. Stop at once if any response or page suggests a charge, an upgrade or an exceeded limit.
8. **Cleanup.** Give each run's users and channels a run-specific prefix. At the end, hard-delete that run's users and channels, and confirm through the API that none remain. Keep the settings and channel-type configuration in place for P06.1-I2, and record them.
9. **README.** The purpose; the variable names read, and by which process; the install, check, live-run and cleanup commands; what a run changes in the application and how to restore it; and what the proof does not show.
10. **Offline unit tests** for the pure logic: token claims, the app-side send check, the matrix definitions and redaction. They must run without the network and without any `STREAM_*` variable.

### 4.2 The matrix quality rule

- Pair every refused case with a positive control: the same request made by an authorized principal (the server, or the right member) succeeds, which shows that the request is well formed.
- A refusal counts only when Stream returns its authentication or permission error. Record the HTTP status and Stream's error code. A 400 or 404 from a malformed request does not count, and neither does a refusal you cannot attribute.
- A case that does not hold is a finding. Report it as it happened, and don't adjust the case to make it pass. If a bypass cannot be closed through configuration, stop that line of work and report it: PF01 treats it as a design blocker.

### 4.3 The evidence record

Create `docs/testing/evidence/2026-09-25-p06-1-chat-provider-proof.md` with a section "P06.1-I1". Include:

- the environment check;
- the SDKs, versions and documentation pages;
- the settings before and after;
- the configuration applied;
- the matrix as a table: case, actor, token, action, expected, observed status and code, control result and verdict;
- the usage counts;
- the cleanup result;
- failures, deviations and limits.

No secrets, tokens or personal data. Synthetic identifiers are fine.

## 5. Checks

Run these and report exact results:

1. `git diff --check <START_SHA> HEAD`, and `git diff --name-only <START_SHA> HEAD` showing only owned paths.
2. Trusted-base classification as in `docs/planning/manager-workflow.md` ("Classification"), with `<START_SHA>` as the base. It should report full scope.
3. Installs from the locks, with the README's commands.
4. The offline unit tests, plus Ruff 0.16.8 (check and format) and mypy 2.3.1 on the Python code, with the README's commands.
5. The live run. Put its results table in the evidence record, and report its start and end times in UTC.
6. The post-run cleanup check.

## 6. Push

Commit on your own session branch only, with clear messages. Push it, and report the branch name and head SHA. Never push to `<MANAGER_BRANCH>` or `main`.

## 7. Report

Report to Nathan, for the manager:

- your branch, `<START_SHA>`, head SHA and tree SHA, and `git diff --stat <START_SHA> HEAD`;
- the environment check (names only);
- the SDKs and versions, and the documentation pages;
- the application settings before and after, and every other change you made in the application;
- the configuration applied, and how to restore the defaults;
- the matrix results: every case with its control and verdict;
- usage counts against the guardrails, and the cleanup result;
- every check with its exact result;
- failures, deviations from this prompt, open questions and limits.

**Stop and report** if:

- an HDE variable is present;
- application 1729640 holds users or channels you did not create;
- anything suggests a charge or an upgrade;
- the secret or a full token appears in any output, log or file. Remove it, and say where it was;
- the work needs a path outside the owned paths.
