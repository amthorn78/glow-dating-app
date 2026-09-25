# P06.1 — Chat-provider permissions and economics proof

**Status: in progress.** Nathan resumed P06.1 on 25 September 2026: *"resume P06.1, yes to reconfiguring the test app"*. App Manager 3 commissioned the first implementation session, P06.1-I1, the same day. The brief is in "Brief — P06.1" below; the sections before it are the proposal and Nathan's answers, kept as the record.

- **Work ID:** P06.1, "Prove chat-provider permissions and economics" (Work Register: Ready). Governing plan: [PF01](../pf-canon/GAPP-PF01-A-to-Z-Implementation-Plan.md), P06 and A08.
- **Owner:** Nathan Amthor. **Manager:** App Manager 3.
- **Why it is next:** after P05, PF01's sequence continues with P06. The [initiation](claude-code-initiation.md) assignment ends: *"Complete the optimization before proposing whether to resume P06.1."* That optimization, M02, is complete.

## Prerequisites reconciled

| Work Register row | State | What it gives P06.1 | Disposition |
|---|---|---|---|
| P02.1: domain state machines and API contracts | Done (PR3) | The contracts P06.1 tests against: F10 unmatch, F11 channel entitlement and message submission, and F13 block and provider revocation. No newly authorized send may begin after a block or unmatch commits, and a provider token alone is not permission ([production contracts](../architecture/production-contracts.md)) | Satisfied |
| P05.3: likes, matches and unmatch | Done at fixture scope (PR14) | An active match plus current pair eligibility, as the input to a later contact decision. `contact_decision()` still returns `send_allowed: False` and `provider_state: "not_configured"`; no provider channel, send or history capability exists ([interactions](../architecture/interactions-fixtures.md#p06-and-p11-handoff)) | Satisfied at fixture scope, which is what P06.1 needs. P11 reruns the send-versus-revocation races with real persistence |
| A08: chat safety enforcement capability | Planned | Nothing yet. A08 is the question P06.1 answers; PF01 says to prove the SDK permission behavior and to change the design or provider if a bypass cannot be closed | Not a precondition; P06.1 resolves it |
| A04: accounts, credentials and approved budget | Planned, access needed | Partly in place: Nathan's development Stream application (`STREAM_APP_ID=1729640`) and its three variables are in the `Glow app` environment, whose network allows `*.stream-io-api.com` and `getstream.io` | The owner inputs below close the rest |

The P05.3 row's next action still routed to App Planner 1's review of AB1-R012; App Manager 3 corrected it in Notion on 25 September. The [AB1-R012 record](../continuity/history/AB1-R012.md) says that the M01 migration read established the report's receipt and that its P06.1 next action is superseded.

## What P06.1 would prove

It runs against the development Stream application with synthetic users only, following steps 2–7 of the [Claude handoff's live-verification sequence](../continuity/claude-code-handoff.md#bounded-live-verification-sequence--after-setup-and-owner-inputs).

- **The authorized path works.** A server-side harness issues user tokens from a server-owned identity mapping and provisions a locked-down one-to-one channel for a matched pair. Two client sessions connect, send and read text, disconnect, reconnect and clean up.
- **No client bypass.** Each client uses its own token directly, as a modified app could. It tries to create channels, join or watch another pair's channel, send, edit, reply, react and attach, and to act with a stale, expired or revoked token. Every attempt must fail.
- **Revocation.** After an unmatch, block, suspension or deletion, no new send succeeds, and history access follows the policy Nathan chooses (input 5). Reconnecting, a send racing the revocation, and a provider outage must all fail closed.
- **Economics.** The plan's actual limits, the pricing that would apply, the usage the proof caused, and whether a paid plan or Maker approval is needed. Nothing is purchased.
- **Records.** The exact variable names, the SDKs and versions chosen from Stream's current documentation, redacted evidence and every failure. The sandbox users and channels are removed at the end.

If a bypass cannot be closed, PF01 treats it as a design blocker: the design or the provider changes before P06.2.

The brief below refines this proposal: sends go through the app server, never directly from a client.

## Proposed shape

- One work item, P06.1, probably in two implementation sessions: first the harness, the authorized path and the bypass matrix; then revocation, history, outage and economics. Each session's head gets its own exact-head review.
- A separate proof harness kept out of the application runtime. The fixture API's guards and the reserved `GLOW_CHAT_API_SECRET` slot stay as they are until a reviewed replacement exists. The brief sets the exact paths and the SDK choices.
- Code and dependency changes are full scope: every Foundation job, an exact-head review, and Codex's review before merge.

**Excluded:** HDE, databases, Railway and production; the mobile chat interface (P06.2); notifications and push (P06.3); webhook endpoints (Stream's before-message-send hook fails open, so it is never the send gate); real people; paid activation; any secret in mobile code, `EXPO_PUBLIC_*` names, logs, the repository or Notion.

## Owner inputs requested (25 September 2026)

None of these is a secret. The API secret stays in the environment settings.

1. **Plan.** The Stream plan of the organization that owns application 1729640: its name, the end date if it is a trial, Maker status if Nathan has applied, and the monthly-active-user and concurrent-connection limits the dashboard shows. *Needed so that the proof stays inside the plan and the economics start from facts.*
2. **Test application and region.** Confirmation that application 1729640 is the proof's test application, that it holds no real users, and that the proof may create and delete synthetic users and channels and change its channel types, roles and permissions; and the application's region. *Needed because the proof reconfigures the application.*
3. **Budget.** Recommended: $0. The proof stays inside the plan's free allowance and stops before any step that would upgrade the plan or incur a charge. Nathan may name a cap instead. *Needed before any live call.*
4. **Secret handling.** Confirmation that the proof may use the three `STREAM_*` values already in the `Glow app` environment, on the server side only. That accepts the recorded risk that any command in those sessions can read the secret ([Claude cloud environments](../continuity/claude-code-handoff.md#claude-cloud-environments)). Staging and production secret storage is decided later, with A04 and P11. *Needed before any live call.*
5. **Chat history after an unmatch or block** (an A05 policy choice). Recommended: afterwards neither person can send or see the conversation, and the history is kept out of sight only for safety reports, with retention decided later under A05. The alternative is a read-only conversation for both. *Needed before the revocation tests, not to start.*

### Answers

- **Inputs 3–5 (Nathan, 25 September 2026): recommendations accepted.**
  - Budget: $0. The proof stays inside the plan's free allowance and stops before any step that would upgrade the plan or incur a charge.
  - Secret handling: the proof may use the three `STREAM_*` values in the `Glow app` environment, on the server side only.
  - Chat history: after an unmatch or block, neither person can send or see the conversation. The history is kept out of sight only for safety reports, and retention is decided later under A05.
- **Inputs 1 and 2: confirmed** from the Stream dashboard by a read-only discovery Nathan ran in Claude in Chrome; see the baseline below. The discovery prompt is pruned; its text is in Git history at `e8494a4`, in `docs/ephemeral/2026-09-25-p06-1-stream-discovery-prompt.md`.
- **Permission (Nathan, 25 September 2026): "yes to reconfiguring the test app".** The proof may create and delete synthetic users and channels and change application 1729640's settings, channel types, roles and permissions.
- **Decision (Nathan, 25 September 2026): "resume P06.1".** The pause is lifted for P06.1; it otherwise stands until Nathan's recorded direction.

## Stream dashboard baseline (25 September 2026, 02:04 UTC)

Facts as the read-only discovery reported them:

- **Application 1729640** is named "Glow Connection System Chat Engine". Its region is US East, its API key matches `qdstwyevnyea`, and it is in Development mode (a "DEV" badge). The secret was shown masked only.
- **Organization** "Glow Connection System" has no other application.
- **Plan:** "Free Chat", billed $0 for 1–30 September. It is not a trial, and no Maker status is shown.
- **Limits:** 1,000 active users; 100 concurrent connections; 2,000,000 API calls a month; 200,000 QueryChannels calls a month; 500,000 stored channels; 5,000,000 stored messages; 5,500,000 total records; 500 GB of outbound traffic a month.
- **Usage, 1–25 September:** 10 API calls; everything else zero.
- **Past a limit:** Stream's general "Fair Usage Limits" document says overages are billed automatically per resource, for example $7 per million API calls and $5 per million stored messages. That is general policy text, not an account-specific statement. The organization has no payment method on file.
- **Data:** no channels and no active users.
- **Safety settings:** "Authentication Checks" and "Permissions Checks" are both shown ON. Their descriptions describe relaxed modes: development tokens accepted from clients, and full permissions for every user regardless of role. **Until the API shows otherwise, treat the application as possibly accepting development tokens and skipping permission checks.**
- **Configuration:** the five default channel types (commerce, gaming, livestream, messaging, team), none custom. Chat roles are not shown in this dashboard. There are no webhooks, and the before-message-send hook is empty.
- **The discovery's actions:** navigation and reading only, except that it opened the application's Edit dialog to read the environment setting and cancelled without saving.

## Brief — P06.1

- **Work ID and title:** P06.1, prove chat-provider permissions and economics. It resolves A08 and supplies the P06 part of A04.
- **Owner and manager:** Nathan Amthor; App Manager 3.
- **Starting commit and manager branch:** manager branch `claude/stoic-carson-66gdig`. Each session's prompt names its start SHA; P06.1-I1 starts from the commit that merged this brief into `main`.
- **Design under proof** (PF01 section 7; contract flows F10, F11 and F13): the server controls channel membership and authorizes every send. A client never sends through Stream directly; the app server sends on the user's behalf after its match and block check. A client's token lets it read its own current match's channel and nothing else.
- **Outcome:** evidence from the live development application, with synthetic users only, that:
  1. Stream's authentication and permission checks are enforced;
  2. the authorized path works: server-issued user tokens with an expiry, server-created one-to-one channels, server-mediated sends and client reads;
  3. no client holding any token can create, join, read or send outside that path, in any channel type, including through edits, reactions, attachments, custom events, profile fields or guest and anonymous access;
  4. after an unmatch, block, suspension or deletion, no new send succeeds and history follows Nathan's policy;
  5. the plan's real limits and costs, and the approvals P06.2 and launch need.

  It also records the exact configuration that achieved this, and how to restore the defaults.
- **Owned paths (writable):** `proofs/stream-chat/**` (new: harness, locks, README and offline tests) and `docs/testing/evidence/2026-09-25-p06-1-chat-provider-proof.md` (new; each session adds its section). P06.1-I2 also owns `docs/architecture/chat-provider-permissions.md`.
- **Manager-owned paths:** this brief and the rest of `docs/planning/`, `docs/continuity/`, `docs/ephemeral/`, `docs/pf-canon/`, root `AGENTS.md` and `CLAUDE.md`, and Notion.
- **Exclusions:** every other path, including `apps/`, `services/`, `packages/`, `scripts/`, `.github/`, `Dockerfile`, `.dockerignore`, `.gitignore` and the `.env.example` files. No change to the fixture API or its guards, and no `GLOW_*` variable set. No database, HDE, Railway or production. Nothing in the Stream organization outside application 1729640. No plan, billing, Maker or team change, no key rotation or region change, no webhook or hook, and no push. No real people or personal data.
- **Dependencies and inputs:** P02.1 and P05.3 are Done. A08 is resolved by this item. A04's P06.1 inputs are supplied: application 1729640 on the Free Chat plan, in US East, with a $0 budget.
- **Budget guardrails:** per session, at most 20 synthetic users, 30 channels, 10 concurrent connections and 5,000 API calls, counted by the harness. Stop before any step that would upgrade the plan or incur a charge.
- **Credential rules:**
  - The server side reads `STREAM_APP_ID`, `STREAM_API_KEY` and `STREAM_API_SECRET` from its own process environment.
  - It never prints, logs or writes the secret or any full token, including into tool configuration files.
  - Client processes run without `STREAM_API_SECRET` in their environment and hold only the API key and their own user token.
  - Evidence may record token claims, never tokens.
- **Matrix quality rule:** every negative case pairs with a positive control, showing that the same request is well formed and succeeds for an authorized principal. A denial counts only when Stream returns its authentication or permission error, recorded by HTTP status and error code. A 400 or 404 from a malformed request does not count.
- **Acceptance checks:**
  1. `git diff --check <START_SHA> HEAD` is clean, and only owned paths changed.
  2. The manager workflow's trusted-base classification reports full scope.
  3. Dependencies install from hash-pinned locks: Python with `pip install --require-hashes`, JavaScript with `npm ci --ignore-scripts`. The harness README gives the exact commands.
  4. The offline unit tests pass. The Python code passes Ruff 0.16.8 and mypy 2.3.1, the versions pinned in `services/api/requirements-dev.lock`.
  5. The README's live-run command completes and prints a redacted results table. Every case's observed result is reported as it happened; a case that does not hold is a failure, not rewritten.
  6. After each run, the application holds none of that run's synthetic users or channels.
- **Classification expectation:** full scope.
- **Evidence home:** `docs/testing/evidence/2026-09-25-p06-1-chat-provider-proof.md`.
- **Report format:** as each session prompt specifies: branch, SHAs, tree, changed paths, every check with exact results, settings before and after, the matrix, usage, cleanup, failures, deviations, open questions and limits.
- **Review plan:** an exact-head code and security review of I1's head in a session Nathan runs, then corrections if needed, then I2, then a delta review of the final head. Every Foundation job must pass on the PR head, and Codex's reviews must finish, before merge.

### Sessions

- **P06.1-I1** ([prompt](../ephemeral/2026-09-25-p06-1-i1-implementation-prompt.md)): enforce and record the checks; lock down every channel type and create the proof's type; prove the authorized path; run the bypass matrix; clean up.
- **P06.1-I2** (written after I1's review): revocation and history under Nathan's policy; suspension and deletion; token expiry and revocation; reconnection and realtime events after revocation; a send racing a revocation; provider outage failing closed; the economics; final cleanup; and `docs/architecture/chat-provider-permissions.md`.

### Reasoning levels

| Session | Manager | TypeSafe v4 | Detail |
|---|---|---|---|
| P06.1-I1 | extra high | extra high | Score 2.99, confidence 0.99. Shape single_session at P 0.53 (new_silent_guard 0.31), so no ultracode under the pre-registered rule. Sent 02:11:41 UTC |

## Risks and limits

- **Intermittent rendered-test failures** (three so far: a form submit that does not advance) can turn P06.1's CI red. The manager cannot re-run jobs, so Nathan re-runs them. The diagnosis is a recorded follow-up.
- **Unverified:** whether the environment's proxy passes Stream's WebSocket connection. The first session checks it.
- **Silent passes:** a bypass test can pass for the wrong reason, for example a malformed request that fails for itself. The matrix quality rule answers this, and the exact-head review checks it.
- **Billing:** the Free Chat plan's limits are far above the guardrails, but Stream's general policy is automatic overage billing and no payment method is on file. Before any real traffic, Nathan settles the billing arrangement (A04).
- **Sandbox scope:** results cover the development application, its plan and synthetic users at the time of the run. Real persistence, concurrency and restore behavior stay with P11. Production credentials and launch pricing are separate.
- **Secret exposure:** every command in a `Glow app` session can read the development secret. If exposure is ever suspected, rotating it in the Stream dashboard and the environment settings is cheap.
