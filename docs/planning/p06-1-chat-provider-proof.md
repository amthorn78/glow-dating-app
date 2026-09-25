# P06.1 — Chat-provider permissions and economics proof

**Status: in progress.** Nathan resumed P06.1 on 25 September 2026: *"resume P06.1, yes to reconfiguring the test app"*. The first implementation session, P06.1-I1, ran the same day; see "P06.1-I1 result".

- It found one bypass that configuration did not close, S15. **Nathan decided S15 the same day:** the display rule, together with a wider product principle. The decision is conditional on the exact-head review confirming S15 live. See "S15: decided".
- The Dev Manager's first reviews, DM-01 and DM-02, are in and considered. This brief applies the accepted changes: I2 is split into I2a and I2b, economics becomes a dashboard discovery, and the harness's checks join CI. See the [review log](../continuity/dev-manager/README.md).
- Next: the Dev Manager reads the revised I1 review prompt (DM-03); then Nathan runs the review.

The brief is in "Brief — P06.1" below. The sections before it are the proposal and Nathan's answers, kept as the record.

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
- **Owned paths (writable):** `proofs/stream-chat/**` (new: harness, locks, README and offline tests) and `docs/testing/evidence/2026-09-25-p06-1-chat-provider-proof.md` (new; each session adds its section). P06.1-I2b also owns `docs/architecture/chat-provider-permissions.md`, and one new job for the harness's offline checks in `.github/workflows/foundation.yml` (DM-02 B6). That workflow change is full scope, under the CI policy's workflow rule.
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
- **Review plan:** an exact-head code and security review of I1's head in a session Nathan runs, then corrections if needed, then I2a and I2b, then a delta review of the final head. Every Foundation job must pass on the PR head, and Codex's reviews must finish, before merge.

### Sessions

- **P06.1-I1** ([prompt](../ephemeral/2026-09-25-p06-1-i1-implementation-prompt.md)): enforce and record the checks; lock down every channel type and create the proof's type; prove the authorized path; run the bypass matrix; clean up. Done on 25 September; see "P06.1-I1 result".
- **Review of I1** ([prompt](../ephemeral/2026-09-25-p06-1-i1-review-prompt.md)): the exact-head code and security review of I1's code head `9ff600f`. It **must** confirm S15 live, because a design decision rests on it (DM-01 P4). It may make one further small live run and changes no configuration. The Dev Manager reads the prompt before Nathan runs it (DM-03).
- **P06.1-I2a, revocation and safety** (live, budgeted; DM-02 B2):
  - **Revocation under Nathan's history policy, by named mechanism:** member removal, a channel-level ban, per-user `revoke_tokens_issued_before`, and hide or freeze. For each, state which of these it ends: REST reads, an **already-open WebSocket subscription**, token reuse and the S15 write. Messages stay retained for safety reports.
  - **Suspension and deletion:** what a hard user delete does to messages and to member custom data needed as safety evidence. This conflicts with Nathan's history policy unless the design says otherwise, so record it plainly.
  - **Tokens and devices:** token expiry, reconnection and cross-device use, with two clients per user.
  - **Send versus revocation, on the provider side only:** a server send attempted after revocation is refused. The database-level ordering is P11's DB06; claim nothing more.
  - **Outage as fault injection:** point the server's Stream client at an unreachable endpoint; the app send path must refuse with no partial state. No real outage is claimed.
  - **The S15 mapping:** which fields a member can set; what the other member receives; whether the server can clear or overwrite member custom data; whether member removal deletes it. The harness checks that the three `member_custom_on_*` settings stay off.
  - **Reruns:** G2 and S10 with the corrected harness; the existence-oracle comparison (existing against non-existent IDs); the fixes not yet exercised live.
  - **Budget:** the prompt sets its own run plan against the 20-user cap and keeps one run in reserve for a rerun.
- **P06.1-I2b, other products, documentation and CI** (live but small):
  - Video and Feeds: what a user token can do, and a lockdown by configuration only. No media session, no push, nothing that could incur a charge.
  - `docs/architecture/chat-provider-permissions.md`, with the exact configuration as a reviewed, reapplicable plan for a future production application (DM-02 B7).
  - The Foundation job for the harness's offline checks (DM-02 B6).
- **Economics** (not an implementation session): a read-only dashboard discovery that Nathan runs, like the baseline, plus Stream's public pricing and terms. It records the plan limits, overage behavior with no payment method on file, any attribution requirement, the data-processing agreement and region (US East against the launch geography, A05) and Maker eligibility.
- **Removed from P06.1:** running the restore command. At P06.1's close, Nathan decides whether the development application stays locked down for P06.2, which is likely, or is restored.
- **Before Nathan runs them:** the Dev Manager reads each live prompt (DM-01 P1).

### P06.1-I1 result

The session ran on 25 September 2026, on branch `claude/compassionate-lamport-531vtk`, from `0f45e64` to head `9ff600f`. Its record is the [evidence record](../testing/evidence/2026-09-25-p06-1-chat-provider-proof.md#p061-i1), and App Manager 3's verification is at its end. The manager integrated the head by fast-forward; draft [PR26](https://github.com/amthorn78/glow-dating-app/pull/26) carries it.

- **Outcome 1, checks enforced: holds.** Both checks were already on.
  - Development, wrong-secret and expired tokens got `401`.
  - Client actions outside the design got `403`, with Stream code 17 or 70.
- **Outcome 2, authorized path: holds,** 18 checks of 18:
  - 900-second tokens and server-created one-to-one channels;
  - app-mediated sends, with refusals that make no Stream call;
  - REST reads, WebSocket delivery, disconnect and reconnect. The environment's proxy passes Stream's WebSocket.
- **Outcome 3, no client bypass: does not hold.** See S15 below.
  - A second channel, free text in typing events, was closed by turning typing events off.
  - Of 85 cases, 68 hold with an attributable refusal. 4 hold because the result is filtered, and 3 because the change is not applied. 9 are inconclusive under the quality rule, and 1 fails.
- **The application's configuration now,** kept for I2a and I2b:
  - guest user creation is disabled;
  - the `user`, `guest` and `anonymous` roles have no application grants;
  - every role's grants are empty in the five default types;
  - in the new `glow-match` type, members may only read, and every content feature is off, typing events included.

  The restore command exists but has not been run.
- **Owner direction during the session.** The application held one user the proof did not create: Stream's dashboard administrator. The session stopped and asked. Nathan answered, at about 03:12 UTC: **"Proceed, leave it (Recommended)"**. The option he chose said three things:
  - the proof never reads, changes or deletes that user;
  - cleanup deletes only the proof's users;
  - the lockdown also empties the admin role's grants in the five default types and `glow-match`.

  So a dashboard feature that acts client-side as that user may be refused there. That is untested.
- **Usage:** 19 of 20 users, 28 of 30 channels, a peak of 5 of 10 connections and 884 of 5,000 API calls. No response suggested a charge.
- **Cleanup:** the application holds only the dashboard user and no channels. One guest user had to be deleted by hand, and the harness was fixed.
- **Not yet exercised live:** the restore command, and the harness fixes made after the final run: prefix matching, the G1 judgement, the R9 control and the guest and anonymous filters.

### S15: decided

**Decision (Nathan, 25 September 2026):** *"I accept your recommendation on S15. There should never be any indication that there is anything happening outside Glow."* The durable record is [ADR 0003](../adr/0003-chat-display-rule.md).

**Conditional on confirmation** (DM-01 P4). The decision rests on I1's own live evidence. The exact-head review must confirm S15 live. If the review narrows S15, or finds a configuration that closes it, the decision returns to Nathan.

- **The design:** option 1 below, the display rule. The app never displays Stream user or member data. Every name, photo and profile field comes from Glow's API, and the app ignores member custom data and `member.updated` events.
- **The principle.** Nathan's second sentence reaches beyond S15. It is a product rule for every provider and every surface. The manager's working reading, which the Dev Manager approved with conditions (DM-02 B1):
  - users never see a sign that anything happens outside Glow;
  - no provider's name, branding, identifiers, error text, notifications or data reaches the user interface;
  - everything a user sees comes from Glow's API, in Glow's own wording.
- **Its scope** (DM-02 B1): Glow's in-app experience and every communication Glow sends: push, email, in-app errors, deep links and the links users share.
- **It binds server and operator consumers too:** Stream member or user custom data is never forwarded into exports, staff or WordPress views, push content or analytics.
- **Proposed carve-outs, for Nathan to confirm** (DM-02 question 1): legally required disclosures (privacy policies, store privacy labels, processor lists, and data-export contents where the law requires recipients), licence notices, and system screens the platform mandates. Until he confirms, no session hides a legally required disclosure or treats a mandated system screen as a defect.
- **The display rule's conditions** (DM-02 B7):
  - I2a shows that member custom data cannot change anything Glow displays or forwards, and that revocation ends the write;
  - deletion and export (PV07) include member custom data held at Stream;
  - I1's configuration becomes a reviewed, reapplicable plan for the production application; the development application's lockdown is not a production control;
  - one channel per person stays the recorded fallback if the first condition fails.
- **Billing** is an open launch gate (A04), not a P06.1 blocker: Stream's general policy bills overages automatically, and no payment method is on file.
- **What follows for P06.1-I2a and I2b:**
  - I2a maps the S15 channel completely: which fields a member can set, what the other member receives, whether the server can clear it and what removal does;
  - I2a keeps the settings that copy member custom data into messages, typing events and mentions off, and checks them in the harness;
  - I2b locks down Stream Video and Feeds, so nothing can ring or notify a user from outside Glow;
  - I2b records, for P06.2, every provider surface a user could otherwise see.
- **What follows for P06.2:** the display rule and its test, opaque Stream user IDs, and provider errors that reach users only as Glow's own messages. Chat state comes from API-served fixtures through the development HTTP client, not from new client-side domain logic (DM-02 B10).

The analysis Nathan decided on is kept below as the record.

#### The finding and the options, as put to Nathan

**The finding.**

- A member's client can write up to 5 KB of free text as custom data on its own membership of its match channel. The call is `updateMemberPartial`, `PATCH /channels/glow-match/{id}/member`, and Stream answered `200`.
- The other member's client receives that text in its ordinary channel query and in a realtime `member.updated` event.
- No Stream permission governs the write. Removing `read-channel-members` hid only the separate members endpoint.
- PF01: *"Provider inability to enforce safety is a design blocker, not a future polish item."* So the design or the provider changes before P06.2. The exact-head review also checks whether configuration can close S15 after all.

**What it can and cannot do.**

- The text never appears in a message. It reaches the other member's app as data, and that person sees it only if the app displays Stream member data.
- It skips the app's moderation and its match and block check, but only while the writer is still a member. Under Nathan's history policy neither person can see the conversation after an unmatch or block. I2 proves how the server ends that access, and whether the write still works afterwards.

**Options.** PF01 requires a design or provider change. Options 1 and 2 are design changes.

1. **A display rule (recommended).**
   - The app never displays Stream user or member data. Every name, photo and profile field comes from Glow's API, and the app ignores member custom data and `member.updated` events.
   - The application settings that copy member custom data into messages, typing events and mentions stay off, and the harness checks them.
   - This relies on the recipient's app, which the writer cannot change. PF01's concern is a client the attacker controls.
   - **Residual risk:** a hidden channel of up to 5 KB between two currently matched people who both run modified apps, which gives them nothing they could not do outside Glow. Unmoderated text is stored at Stream, and nobody sees it in the app.
   - **Cost:** the rule and its test in P06.2. I2 maps the channel: which fields a member can set, what the other member receives, whether the server can clear it, and what removal does.
2. **One channel per person.**
   - Each person in a match gets a channel with only themselves as a member, and the server writes every message into both.
   - A member's own data then reaches nobody else. That closes S15 at the provider level, which is PF01's wording. It also removes the one client-chosen value a read event carries, the message ID.
   - **Costs:** two writes per message and two channels per match; read receipts relayed by the server or dropped; more server logic. I2 must prove the pattern: a server send into a channel the sender is not a member of, reads, events, unread counts and revocation.
3. **Clearing the data by webhook.** It acts after the other member has already received the data, so it does not close S15. At most it is a supplement.
4. **Another provider.** Not recommended. No other case failed; the nine inconclusive cases are rerun in I2 where they matter.

Separately, Nathan may ask Stream support whether client writes to member custom data can be disabled. If they can, configuration closes S15.

**Manager's recommendation: option 1**, unless the review finds a configuration that closes S15. Option 2 is the fallback if I2 shows that member data can change anything the app displays, or if Nathan wants the closure at the provider level.

### I1's open questions: manager dispositions

1. **S15:** decided by Nathan on 25 September 2026: the display rule, with the principle recorded under "S15: decided".
2. **Video and Feeds: yes, within P06.1.** PF01 puts voice, video and public feeds outside the initial release, so the app will not display them. A modified client could still use them with its user token, for example to ring the other member, or to run calls billed to Glow's Stream organization. I2b records what a user token can do there and locks it down through configuration. It opens no media session, sets up no push and does nothing that could incur a charge.
3. **Guest reach (G2) and the poll vote (S10): yes.** I2a reruns them with the corrected harness and a fresh budget, together with the other fixes not yet exercised live.
4. **Unguessable IDs: yes, a P06.2 requirement.** Stream user IDs are random and opaque, never derived from Glow's account IDs, names or emails, and never shown to other users. I2a records whether a refusal for an existing ID differs from one for an ID that does not exist.

### Reasoning levels

Each prompt's header gives its recommended level. The readings and outcomes are kept only in the Notion page *TypeSafe effort scorer — Glow app usage log* (DM-01 P8). Both rows for this item, P06.1-I1 and the review of I1, are there.

## Risks and limits

- **Intermittent rendered-test failures** (three so far: a form submit that does not advance) can turn P06.1's CI red. The manager cannot re-run jobs, so Nathan re-runs them. The diagnosis is a recorded follow-up.
- **S15** is decided: the display rule. Its residual risk stays recorded under "S15: decided", and P06.2 must enforce the rule with a test.
- **WebSocket:** verified by I1. The environment's proxy passes Stream's WebSocket: connect, events, disconnect and reconnect.
- **The dashboard side effect,** which Nathan accepted: the admin role has no grants in the default types or `glow-match`. Restoring the recorded baseline returns the default types' grants.
- **Silent passes:** a bypass test can pass for the wrong reason, for example a malformed request that fails for itself. The matrix quality rule answers this, and the exact-head review checks it.
- **Billing:** the Free Chat plan's limits are far above the guardrails, but Stream's general policy is automatic overage billing and no payment method is on file. Before any real traffic, Nathan settles the billing arrangement (A04).
- **Sandbox scope:** results cover the development application, its plan and synthetic users at the time of the run. Real persistence, concurrency and restore behavior stay with P11. Production credentials and launch pricing are separate.
- **Secret exposure:** every command in a `Glow app` session can read the development secret. If exposure is ever suspected, rotating it in the Stream dashboard and the environment settings is cheap.
