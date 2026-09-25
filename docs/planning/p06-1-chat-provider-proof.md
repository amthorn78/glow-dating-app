# P06.1 — Chat-provider permissions and economics proof

**Status: proposed, not dispatched.** App Manager 3 gave Nathan this proposal on 25 September 2026. Feature work stays paused until Nathan's recorded direction resumes it. If he resumes P06.1, its persistent brief is added to this file and its prompt goes in `docs/ephemeral/`, following the [manager workflow](manager-workflow.md).

- **Work ID:** P06.1, "Prove chat-provider permissions and economics" (Work Register: Planned). Governing plan: [PF01](../pf-canon/GAPP-PF01-A-to-Z-Implementation-Plan.md), P06 and A08.
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

Nathan's decision and each input are recorded here, with the date, when he answers.

## Risks and limits

- **Intermittent rendered-test failures** (three so far: a form submit that does not advance) can turn P06.1's CI red. The manager cannot re-run jobs, so Nathan re-runs them. The diagnosis is a recorded follow-up.
- **Unverified:** whether the environment's proxy passes Stream's WebSocket connection. The first session checks it.
- **Sandbox scope:** results cover the development application, its plan and synthetic users at the time of the run. Real persistence, concurrency and restore behavior stay with P11. Production credentials and launch pricing are separate.
- **Secret exposure:** every command in a `Glow app` session can read the development secret. If exposure is ever suspected, rotating it in the Stream dashboard and the environment settings is cheap.
