# P06.1 — Chat-provider permissions and economics proof

**Status: in progress.** Nathan resumed P06.1 on 25 September 2026: *"resume P06.1, yes to reconfiguring the test app"*. The first implementation session, P06.1-I1, ran the same day; see "P06.1-I1 result".

- It found one bypass that configuration did not close, S15. **Nathan decided S15 the same day:** the display rule, together with a wider product principle. The exact-head review confirmed S15 live on 25 September, so the display rule stands as S15's answer. The principle is in force (DM-03 G4), and Nathan confirmed its exceptions (OD-16). See "S15: decided".
- The Dev Manager's first reviews, DM-01 and DM-02, are in and considered. This brief applies the accepted changes: I2 is split into I2a and I2b, economics becomes a dashboard discovery, and the harness's checks join CI. See the [review log](../continuity/dev-manager/README.md).
- The Dev Manager read the revised I1 review prompt (DM-03) and approved it with conditions. Revision 3 applies them.
- **Nathan's answers of 25 September** (OD-16 to OD-24) change this item in three ways:
  - the S15 exceptions are confirmed (OD-16);
  - the intermittent rendered-test failure is diagnosed now, inside P06.1 (OD-21);
  - the Stream secret's handling in cloud sessions is settled before I2a (OD-20).
- **The process is linear** (OD-29): one session at a time. The flake diagnosis is done: the cause was a focus race in the app's own code, fixed inside P06.1 and integrated at `8b8b1bd` (see "Sessions"). The I1 review is done: S15 is confirmed, and the verdict is "changes required". The exact-head review of the fix approved it on 26 September, so OD-21's acceptance is met. The correction pass P06.1-C1 is done: verified and integrated at `e85bba0`. Its exact-head review approved it on 26 September and left three should-fix findings and seven nits. The second offline correction pass, P06.1-C2, fixed them: verified and integrated at `63e922f`. Its exact-head review approved it on 26 September and left two should-fix findings and eight nits. The third offline correction pass, P06.1-C3, fixed them, with the RT2 and RT3 change: verified and integrated at `8c1a8c0`. Its exact-head review approved it on 26 September and left six nits and one gap, which go into I2a's offline first step. The Dev Manager read I2a's prompt (DM-04) and approved it with conditions, which revision 2 applies. I2a, the live revocation and safety slice, is done: verified and integrated at `6a51dae`. No Stream mechanism meets the history policy on its own. Its exact-head review approved it on 27 September and left two should-fix findings and four nits, which go into I2b's offline first step; finding 1 is fixed there before any live call. The Dev Manager read I2b's prompt (DM-05) and approved it with conditions; revision 2 applied them. I2b, the last live session, is done: verified and integrated at `55b2238`; the Video and Feeds lockdown is applied to the development application, and the architecture document P06.2 designs from is written. Its exact-head review approved it on 27 September and confirmed both design decisions that rest on its live results. It left two should-fix findings and eight nits; finding 1 falls, narrowly, in the class that gets an offline correction pass before P06.1 closes. P06.1-C4 fixed all ten offline, with what its own review found in its first fixes: verified and integrated by fast-forward at `c83bedf` (code head `b2b9a0b`). Its exact-head review asked for changes: one should-fix finding in the correction class (`validate` misses stream-chat methods that can steer a request) and four nits. P06.1-C5, a small offline correction pass, fixed the finding and three of the nits (the fourth, ADR 0003's wording, was the manager's), with what it and its own review found: verified and integrated by fast-forward at `1a5f58a` (code head `11b5771`). Its exact-head review, P06.1's final delta review, approved it on 28 September with three nits, recorded; the manager corrected nit 1's wording. The Dev Manager read the economics discovery's prompt (DM-06) and approved it with conditions, which revision 2 applies; the discovery is next.
- **The Stream secret is settled** (OD-28): Nathan adds the three `STREAM_*` variables for each session that calls Stream, starts it, then deletes them.

The brief is in "Brief — P06.1" below. The sections before it are the proposal and Nathan's answers, kept as the record.

- **Work ID:** P06.1, "Prove chat-provider permissions and economics" (Work Register: Ready). Governing plan: [PF01](../pf-canon/GAPP-PF01-A-to-Z-Implementation-Plan.md), P06 and A08.
- **Owner:** Nathan Amthor. **Manager:** App Manager 5 from 27 September 2026, started by Nathan by hand; App Manager 4 before it that day (OD-31); App Manager 3 until then.
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
4. **Secret handling.** Confirmation that the proof may use the three `STREAM_*` values already in the `Glow app` environment, on the server side only. That accepts the recorded risk that any command in those sessions can read the secret ([Claude cloud environments](../operations/environment-inventory.md#claude-cloud-environments)). Staging and production secret storage is decided later, with A04 and P11. *Needed before any live call.*
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
- **Owner and manager:** Nathan Amthor; App Manager 5 from 27 September 2026; App Manager 4 before it that day (OD-31), and App Manager 3 before that.
- **Starting commit and manager branch:** manager branch `claude/magical-wozniak-yfmmx2` (draft [PR27](https://github.com/amthorn78/glow-dating-app/pull/27)) from 27 September 2026, continuing `claude/stoic-carson-66gdig` (PR26) from its head `2a86c8e`. Each session's prompt names its start SHA; P06.1-I1 starts from the commit that merged this brief into `main`.
- **Design under proof** (PF01 section 7; contract flows F10, F11 and F13): the server controls channel membership and authorizes every send. A client never sends through Stream directly; the app server sends on the user's behalf after its match and block check. A client's token lets it read its own current match's channel and nothing else.
- **Outcome:** evidence from the live development application, with synthetic users only, that:
  1. Stream's authentication and permission checks are enforced;
  2. the authorized path works: server-issued user tokens with an expiry, server-created one-to-one channels, server-mediated sends and client reads;
  3. no client holding any token can create, join, read or send outside that path, in any channel type, including through edits, reactions, attachments, custom events, profile fields or guest and anonymous access;
  4. after an unmatch, block, suspension or deletion, no new send succeeds and history follows Nathan's policy;
  5. the plan's real limits and costs, and the approvals P06.2 and launch need.

  It also records the exact configuration that achieved this, and how to restore the defaults.
- **Owned paths (writable):** `proofs/stream-chat/**` (new: harness, locks, README and offline tests) and `docs/testing/evidence/2026-09-25-p06-1-chat-provider-proof.md` (new; each session adds its section). P06.1-I2b also owns `docs/architecture/chat-provider-permissions.md`, and one new job for the harness's offline checks in `.github/workflows/foundation.yml` (DM-02 B6). That workflow change is full scope, under the CI policy's workflow rule.
  - **The flake diagnosis** (OD-21) owns `docs/testing/evidence/2026-09-25-p06-1-rendered-flake-diagnosis.md`.
  - Only if it proves a cause, it also owns the files under `apps/mobile/src/` and `apps/mobile/rendered/` that the fix requires. That is full scope.
- **Manager-owned paths:** this brief and the rest of `docs/planning/`, `docs/continuity/`, `docs/ephemeral/`, `docs/pf-canon/`, root `AGENTS.md` and `CLAUDE.md`, and Notion.
- **Exclusions:** every other path, including `apps/` (except what the flake diagnosis's proven fix requires), `services/`, `packages/`, `scripts/`, `.github/` (except the one Foundation job P06.1-I2b owns; DM-03 E1), `Dockerfile`, `.dockerignore`, `.gitignore` and the `.env.example` files. No change to the fixture API or its guards, and no `GLOW_*` variable set. No database, HDE, Railway or production. Nothing in the Stream organization outside application 1729640. No plan, billing, Maker or team change, no key rotation or region change, no webhook or hook, and no push. No real people or personal data.
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
  - **Result (25 September; Nathan ran it at max):** changes required. S15 is confirmed live, and no configuration closes it. Two blocking findings must be fixed before I2a runs live on the harness: a verdict can come from an SDK error instead of Stream's answer, and a failed restore of a temporary change does not stop the run. Findings 3 to 9 go into the same correction pass. No recorded I1 result changes. See the evidence record, "Exact-head review of I1".
- **P06.1-I2a, revocation and safety** (done: Nathan ran it on 26 September, at max; live, budgeted; DM-02 B2; OD-29; [prompt](../ephemeral/2026-09-26-p06-1-i2a-implementation-prompt.md)). The Dev Manager read revision 1 and approved it with conditions (DM-04); revision 2 applies them. Nathan adds the Stream variables and runs it.
  - **Revocation under Nathan's history policy, by named mechanism:** member removal, a channel-level ban, per-user `revoke_tokens_issued_before`, and hide or freeze. For each, state which of these it ends: REST reads, an **already-open WebSocket subscription**, token reuse and the S15 write. Messages stay retained for safety reports. Also, for each: whether the affected member's own client can undo it, and what each member is shown, meaning the event types, any system message and whether it names who acted (DM-04 finding 6).
  - **Suspension and deletion:** what a hard user delete does to messages and to member custom data needed as safety evidence. This conflicts with Nathan's history policy unless the design says otherwise, so record it plainly.
  - **Tokens and devices:** token expiry, reconnection and cross-device use, with two clients per user.
  - **Send versus revocation, on the provider side only:** a server send attempted after revocation is refused. The database-level ordering is P11's DB06; claim nothing more.
  - **Outage as fault injection:** point the server's Stream client at an unreachable endpoint; the app send path must refuse with no partial state. No real outage is claimed.
  - **The S15 mapping:** which fields a member can set; what the other member receives, and in which event types, with the SDK's local events excluded (finding 4); whether the server can clear or overwrite member custom data; whether member removal deletes it. The harness checks that the three `member_custom_on_*` settings stay off.
  - **Reruns:** the existence-oracle comparison (existing against non-existent IDs), and the fixes not yet exercised live.
  - **C1's, C2's and C3's fixes, first used live here.** The evidence record's "What P06.1-I2a must know" lists, C1's, C2's and C3's, name them, the three new server calls whose answer shapes I2a records, and the exit codes. Anything the harness reports as not verified is reported, never bypassed.
  - **Before any live run, offline:** the C3 review's six nits and the gap it found. Nit 1, the gap and nit 2(a) are required; the rest are fixed or left with a reason. See the evidence record, "Exact-head review of C3", and its disposition. DM-04 adds a guard in code for destructive calls, closing checks that see application-wide settings, and an independent review pass inside I2a before its first live call (findings 1, 2 and 7).
  - **G2 and S10, with new setups** (the I1 review's finding 6). G2's guest is created on the server side (`ServerApi.create_guest`) and connects by its ID only, because the lockdown refuses the connect `setGuestUser` makes. S10 needs a new setup, because its type-level toggle did not reach the channel in time.
  - **Endpoints the I1 matrix never tried** (finding 9). Content in front of the other member: `updateAIState`, `partialUpdateMember` on the other member, `pin` and `archive`, invites, leaving with a message, and a ban or shadow ban. Reads outside the match: `sync`, replies, reactions and messages by ID, `queryReactions`, `getThread` and `queryMessageHistory`.
  - **Budget:** the prompt sets its own run plan against the 20-user cap and keeps one run in reserve for a rerun. The session counts the complete set offline before any live call. Run 1 may use that count if what is left covers one rerun, and no channel or user is shared between mechanisms to fit a number (DM-04 finding 5).
  - **Outage injection** stays inside the process: a transport that raises a connection error, so no request leaves it. In this environment the egress proxy listens on a loopback address (DM-04 finding 3).
  - **Result (26 September; branch `claude/p06-1-i2a-revocation-safety-wms9ea`, head `761fa28`, code head `7ce93cc`):** step 1 and the new cases were built offline, and an independent check before the first live call found 2 blocking findings and 7 more, all fixed. Run 1 stopped before any case: C1's reply matching, at its first live use, ended a client session. I2a fixed that offline and used its one reserve rerun for all 114 cases, with no charge or limit signal and a complete cleanup; no live run remains. The unit tests went from 252 to 393, and the fix reversals from 147 to 242. The manager verified the branch and integrated it at `6a51dae`. Push run 36278363805 and PR run 36278366585 on `6a51dae` passed all six jobs; the rendered suite passed 84 of 84.
    - **No Stream mechanism meets the history policy on its own.** Removal comes closest; a channel ban, hide and freeze leave the member reading; per-user revocation ends existing tokens, but a new token works; deactivation locks the user out account-wide; a hard delete removes the history, and an old token can re-create the user.
    - **Also for P06.2:** free-text paths to the other member (invites answered with a message, AI-indicator events, pin and archive flags, a write to the other member's membership), existence oracles, and an open connection that outlives its token. See the evidence record, "P06.1-I2a", "What I2b and P06.2 must know".
    - **The manager's decisions** on what I2a left open: two proposed rules for I2b's runs, whether a term the request itself carried counts as disclosed and when a 404 code 16 counts as ended; an approach to the poll listing; and three deviations accepted. See the manager's verification of I2a. A design decision that rests on I2a's findings stays conditional until a review confirms it live (DM-01 P4).
- **Review of I2a** (done; OD-29; [prompt](../ephemeral/2026-09-26-p06-1-i2a-review-prompt.md)). An offline exact-head review of the merge commit `6a51dae`, scoped to I2a's change. It needed no Stream variables and no Dev Manager read. It also assessed the manager's two proposed rules.
  - After it, only a blocking finding, or a should-fix finding that could create a false HOLDS or a false "ended", lose an observed FAIL or DOES NOT MEET, send a request after a charge or limit signal, or let a change escape the guard, delays I2b's live runs. Other findings go into I2b's offline first step.
  - **Result (27 September; Nathan ran it at extra high):** approve. The C3 review's items, DM-04's conditions and the independent check's findings are confirmed fixed. The product findings are sound, but the hard delete's re-creation of the user is inferred. Two should-fix findings and four nits remain, and no recorded result changes:
    - **finding 1** falls narrowly in the class above: an interruption inside a family step loses that step's observations, so a DOES NOT MEET could become INCONCLUSIVE, never a pass. It delays I2b's live runs, not the start of I2b: I2b fixes it offline, with a test, and its independent check confirms the fix before any live call;
    - **finding 2:** two identical successes can differ in size, so the existence oracle can report a false FAIL.

    The reviewer agrees with the manager's decisions, with one detail for the disclosure rule and one refinement for 404 code 16. See the evidence record, "Exact-head review of I2a", and its disposition.
- **P06.1-I2b, other products, documentation and CI** (live; revision 1 written on 27 September for the Dev Manager's read, DM-05, which approved it with conditions; revision 2 applies them as written and needs no further read (DM-03 G2); [prompt](../ephemeral/2026-09-27-p06-1-i2b-implementation-prompt.md)):
  - Video and Feeds: what a user token can do, and a lockdown by configuration only. No media session, no push, nothing that could incur a charge.
  - `docs/architecture/chat-provider-permissions.md`, with the exact configuration as a reviewed, reapplicable plan for a future production application (DM-02 B7).
  - The Foundation job for the harness's offline checks (DM-02 B6).
  - **From I2a** (the manager's verification of I2a): the two rules, as the review of I2a left them; both normalized messages kept in each existence-oracle pair, and a `sync` pair added; the poll listing; the API key removed from free text in outputs; and live reruns of RV-remove and SD-deactivate under the rule for 404 code 16, which I2b's review confirms.
  - **From the review of I2a,** in the offline first step: its two should-fix findings and four nits, as its disposition sets. Finding 1's fix is confirmed before any live call.
  - Its prompt's Dev Manager read also covered M1 and M2 shared by the four channel-level mechanisms, which the manager accepted for I2a: the manager's reading is the one the Dev Manager meant, stated in four parts (DM-05 finding 7).
  - **Its live work** (revision 2; DM-05 findings 1, 2 and 6): run 1 reruns RV-remove, SD-deactivate, F9-thread, F9-sync and the existence oracle under the new rules, with S3a as a live check of the guard's new message rule; an availability probe, one read per product, decides whether Video's and Feeds' cases run at all, and a product-not-enabled answer is a finding, not a charge signal; run V1 tries Video and Feeds with user tokens; the Video and Feeds baseline is committed; the lockdown is applied by a scoped, differential `configure --products video,feeds --apply` once, only if run V1 shows a capability to remove, and only when its dry run lists nothing but Video and Feeds and chat verifies, which the command checks in code; run V2 tries them again. The count covers run 1, V1, V2 and the largest rerun; one rerun is in reserve.
  - **In code, not prose** (DM-05 finding 3): the runner's Video and Feeds op and the guard's new scope carry an allowlist and a deny-list (no ring, notify, join, recording, broadcast, transcription or caption), and a case is made only if its object has a server-side delete.
  - **The architecture document** also tables every path a modified client has to the other member with its closure, and gives ADR 0003's four conditions their status per mechanism (DM-05 finding 5). The manager updates ADR 0003 and the CI policy's job counts after I2b's review (DM-05 findings 4 (c) and 5 (b)).
  - **Result (27 September; Nathan ran it on Fable 5.1 at extra high; branch `claude/confident-brown-baykju`, head `0a0512c`, code head `ad89753`):** done, from revision 2. Step 1 and step 2 were built offline (`bca64eb`, `a1880fb`); the independent check found six items and three limits, fixed or recorded at `2ff6807`. Fifteen live commands, one at a time, each from a committed and pushed head at which the offline checks and the fix reversals passed; no charge or limit signal, every cleanup complete. Run 1: RV-remove and SD-deactivate **MEET the history policy** under the 404 code 16 rule; EO-channel (also through `sync`, by shape) and EO-message FAIL as oracles; EO-user HOLDS; F9-sync HOLDS (filtered); F9-thread INCONCLUSIVE (no thread can exist with replies off); S3a HOLDS. The probe found both products available. Run V1 first exposed a harness defect (Stream never recreates a deleted feed ID), fixed at `93390ce`; the reserve rerun then showed what a `user` token could do with the application's default grants: **16 of 18 cases FAIL** (create calls, read and query other users' calls, send custom events, post activities, read and query other users' feeds, follow, comment, react). The **lockdown was applied once** at 05:58:31 UTC (nine `PUT`s, each 201, re-read verified) and recorded at `ad89753`, from which every run verifies it. Run V2: **9 HOLDS, 7 FAIL, 2 INCONCLUSIVE**: what remains is held by a call's member or creator and a feed's creator, which the plan does not touch and which Glow's server never creates for a user, and the activities query still returns another user's activities, which no configuration in the plan removes; recorded as open. The unit tests went from 393 to 503, the fix reversals from 242 to 342. The Foundation job "Stream proof checks" ran and passed on every push. The manager verified the branch and integrated it at `55b2238`; see the evidence record, "P06.1-I2b" and the manager's verification under it, and the [architecture document](../architecture/chat-provider-permissions.md).
- **Review of I2b** (done; Nathan ran it on 27 September on Fable 5.1 at max, from revision 3 of its prompt at `edbe592`; OD-29; [prompt](../ephemeral/2026-09-27-p06-1-i2b-review-prompt.md)). An offline exact-head review of the merge commit `55b2238`, scoped to I2b's change: the harness, the workflow and the architecture document. It needs no Stream variables and no Dev Manager read. Two design decisions rest on I2b's live results and stay conditional until it confirms them (DM-01 P4): removal and deactivation meeting the history policy under the 404 code 16 rule, and what a user token can do in Video and Feeds before and after the lockdown. After it, only a blocking finding, or a should-fix finding that could create a false HOLDS, MEETS or "ended", lose an observed FAIL, send a request after a signal, let a change escape the guard or the deny-lists, or let the scoped `configure` apply anything outside the two products, gets a correction pass before P06.1 closes; other findings go into the final delta review or the records. The manager then updates ADR 0003's conditions (DM-05 finding 5 (b)); the CI policy's job names and counts are updated at I2b's integration (DM-05 finding 4 (c)).
  - **Result (27 September):** approve. I2b's harness, records and architecture document are sound, and no recorded result changes. Both design decisions that rest on I2b's live results are confirmed: removal and deactivation meet the history policy under the 404 code 16 rule, and the record of what a user token can and cannot do in Video and Feeds before and after the lockdown stands. Two should-fix findings and eight nits remain. Finding 1 falls, narrowly, in the class above: the runner's generic `call` op can reach Video and Feeds endpoints without the product op's allowlist or deny-list. Finding 2: the lockdown's verification and its record cover only the client roles' grants. The manager updated ADR 0003's conditions and "Revisit when", and marked I2b's claims in the architecture document as confirmed. See the evidence record, "Exact-head review of I2b".
- **P06.1-C4, the fourth correction pass** (done; Nathan ran it on 27 September on Opus 5.5 at high; OD-29; [prompt](../ephemeral/2026-09-27-p06-1-c4-correction-prompt.md)).
  - One offline implementation session fixes the I2b review's two findings and eight nits, and brings the README and the architecture document into line. Each code fix gets a test that fails without it and a reversal.
  - Finding 1 comes first: no request to a Video or Feeds path leaves the runner unless the product op's check allows it, whatever op sent it.
  - It makes no live run and no Stream call, so it needs no Stream variables and no Dev Manager read.
  - Its exact-head review follows, offline, and is P06.1's final delta review. (It asked for changes, so C5's review is now the final delta review.)
  - **Result (27 September; branch `claude/festive-ritchie-31vt3v`, head `c83bedf`, code head `b2b9a0b`):** the two findings and eight nits are fixed offline, each code fix with a test that fails without it and a reversal. Nothing reaches Video or Feeds except through the product op's check, whatever op sends the request; the lockdown's verification compares every role and setting with the committed baseline; a configure apply always leaves its record and sends nothing after a charge or limit signal. C4's own review sub-agent found a blocking gap in the first fix of finding 1 (a percent-escape that is not UTF-8 switched the new check off), a should-fix in nit 8's fix and ten further items; C4 fixed them all, each with a test and a reversal except `maxRedirects: 0`. The unit tests went from 503 to 543 and the fix reversals from 342 to 378. The manager verified the branch, re-ran the offline checks and the whole reversal set, and integrated it by fast-forward; see the evidence record, "P06.1-C4 corrections" and the manager's verification under it.
- **Review of C4** (done; Nathan ran it on 27 September; OD-29; [prompt](../ephemeral/2026-09-27-p06-1-c4-review-prompt.md)). An offline exact-head review of C4's head `c83bedf`, scoped to C4's change: P06.1's final delta review. It needs no Stream variables and no Dev Manager read. After it, only a blocking finding, or a should-fix finding that could create a false HOLDS, MEETS or "ended", lose an observed FAIL or DOES NOT MEET, send a request after a charge or limit signal, let a request or a change escape the runner's new check, the guard or the deny-lists, or let the scoped `configure` apply anything outside the two products, gets another offline correction pass; other findings go into the records.
  - **Result (27 September):** changes required. C4's change is sound apart from one should-fix finding, which the review places, narrowly, in the correction class: `matrix.validate` does not refuse every stream-chat method whose arguments reach a request's configuration or path (a request-options argument, the channel target, the reminder methods), and the README's recorded limits rest on it doing so. No current step or harness call reaches such an argument. Four nits: `maxRedirects: 0` has no test; ADR 0003's condition (c) still said "until P06.1-C4" (the manager's, fixed in its records); a failed record write after a signal loses the stop's exit code; one ledger-rule test shows less than its name. The manager verified the report and recorded it in the evidence record, "Exact-head review of C4".
- **P06.1-C5, the fifth correction pass** (done; Nathan started it on 27 September on Opus 5.5 at high; OD-29; [prompt](../ephemeral/2026-09-27-p06-1-c5-correction-prompt.md)).
  - One small offline implementation session: `validate` becomes an allowlist of the (target, method, maximum positional arguments) the matrix uses; the runner also refuses the request-rewriting headers, whatever op sends the request (the manager's addition); the README and C4's record say what remains. Nits 2, 4 and 5 ride with it. Each code fix gets a test that fails without it and a reversal.
  - It makes no live run and no Stream call, so it needs no Stream variables and no Dev Manager read.
  - It lands, with its review, before any further live use of the harness.
  - **Result (28 September; branch `claude/zealous-gauss-bgnir3`, head `1a5f58a`, code head `11b5771`):** finding 1, with the manager's addition, and nits 2, 4 and 5 are fixed offline, each code fix with a test that fails without it and a reversal. `validate` refuses every `call` step outside an allowlist of the 39 (target, method, maximum positional arguments) the matrix uses, and the client's reminder methods always; the runner refuses five request-rewriting headers on every request, reading each header name as it is sent; after a charge or limit signal the command exits 3 whatever replaced its stop, except a Ctrl-C, and a failed record write keeps that stop. C5's own review found three should-fix items and three nits: C5 fixed or recorded each, and left two proposals, which the manager did not take in P06.1. The unit tests went from 543 to 570 and the fix reversals from 378 to 391. The manager verified the branch, re-ran the offline checks and the whole reversal set, and integrated it by fast-forward; see the evidence record, "P06.1-C5 corrections" and the manager's verification under it.
- **Review of C5** (done; Nathan ran it on 28 September on Opus 5.5 at extra high; OD-29; [prompt](../ephemeral/2026-09-28-p06-1-c5-review-prompt.md)). An offline exact-head review of C5's head `1a5f58a`, scoped to C5's change: P06.1's final delta review. It needs no Stream variables and no Dev Manager read. After it, only a blocking finding, or a should-fix finding that could create a false HOLDS, MEETS or "ended", lose an observed FAIL or DOES NOT MEET, send a request after a charge or limit signal, let a request or a change escape the runner's check, the guard or the deny-lists, or let the scoped `configure` apply anything outside the two products, gets another offline correction pass; other findings go into the records.
  - **Result (28 September):** approve. C5's change and its records are sound, and no finding falls in the class above. Three nits:
    - the records said JSON nested two levels deep in a query value is reachable only through a request-options argument, but a `product` step's `params` can carry it too. The manager corrected the README and the evidence record in place (AM5-06);
    - a C4 clause that now matters only for a budget stop in the re-read has no test;
    - without a signal, `finish()` chains an apply failure to a later re-read error.

    Nits 2 and 3 go to the harness's next use, with the review's advice to reconsider an allowlist of header names before the harness is used live again. The manager verified the report and recorded it in the evidence record, "Exact-head review of C5".
- **Economics** (not an implementation session; [prompt](../ephemeral/2026-09-28-p06-1-economics-discovery-prompt.md), revision 2). The Dev Manager read revision 1 and approved it with conditions ([DM-06](../continuity/dev-manager/reviews/2026-09-28-dm-06-economics-discovery-prompt-read.md); [consultation](../ephemeral/2026-09-28-dm-06-economics-discovery-prompt-read.md)); revision 2 applies them as written and needs no further read (DM-03 G2). A read-only dashboard discovery that Nathan runs in Claude in Chrome, like the baseline, plus Stream's public pricing and terms. It records the plan limits, overage behavior with no payment method on file, any attribution requirement, the data-processing agreement and region (US East against the launch geography, A05) and Maker eligibility.
  - **DM-06 adds:** the usage for 1 to 30 September 2026, the period P06.1's live runs fell in, and the next period's if one has begun; what the application's Development mode (the "DEV" badge) limits and what moving to production requires; whether the free plan and the Maker program may serve a commercial app in production, and any kind of app they exclude; the data-processing agreement's transfer mechanism, data retention, and the notice before a price change. The session stays on Stream's two sites, opens only the dashboard pages the items need, clicks only links, menus, tabs and view pickers, and types, submits, downloads and records nothing; each fact is marked account-specific or general policy.
  - **The manager's verification** (DM-06 finding 5 (d)): it compares September's API calls with the usage the P06.1 sessions' ledgers recorded, and the stored channels and messages with the cleanups' "nothing remaining"; a large difference either way gets a line in the record.
  - **What goes to Nathan** (DM-06 finding 5 (e)): an attribution requirement is not a legally required disclosure, and only Nathan adds an exception to the display rule (ADR 0003, decision 4 and "Revisit when"; OD-16). Such a requirement, a Maker or terms exclusion of dating apps, or a production-use limit goes to him as a decision in OD-32's form, with the Dev Manager's text; the manager does not classify it. It bears on A04 and R04.
  - **Maker status** (OD-22): Nathan submitted the Maker Account application by 25 September 2026. Stream's review takes about two weeks, which is an estimate, not an approval date, and no separate submission confirmation has been seen. The discovery checks the application's status in the dashboard.
  - Nothing is assumed about approval or its terms. The $0 budget stands (OD-12).
- **Removed from P06.1:** running the restore command. At P06.1's close, Nathan decides whether the development application stays locked down for P06.2, which is likely, or is restored.
- **Before Nathan runs them:** the Dev Manager reads each live prompt (DM-01 P1).
- **Rendered-test flake diagnosis** (OD-21; [prompt](../ephemeral/2026-09-25-p06-1-flake-diagnosis-prompt.md)). Nathan directed it now, inside P06.1, because a red occurrence would stop PR26 being verified. It is the first session in the linear order (OD-29): Nathan started it on 25 September, at max. The I1 review follows it.
  - The session diagnoses the intermittent failure where a form submit does not advance.
  - It fixes the failure only if it proves the cause, and never by weakening assertions, raising timeouts or adding retries.
  - A passing rerun resolves nothing.
  - If the cause is unrelated to P06.1 and cannot turn PR26's CI red, the fix becomes a focused repair item.
  - **Result (25 September; branch `claude/trusting-mayer-bw6p40`, head `a7ab30b`):** cause class (a), a defect in the app's code. On web, `focusText` moved focus to the screen heading or the error alert one frame after they appeared; when a test had just focused a field, the entry that followed was erased, so the submit stayed put with an alert. The fix leaves focus in a shown text field that already has it, with a regression test. Route: fixed inside P06.1. The manager verified the report and integrated it at `8b8b1bd`; see the [evidence record](../testing/evidence/2026-09-25-p06-1-rendered-flake-diagnosis.md), "Manager verification".
- **Review of the flake fix** (done; OD-29; [prompt](../ephemeral/2026-09-26-p06-1-flake-fix-review-prompt.md)). The fix is new code in PR26, so it needed its own exact-head review of code head `8b8b1bd` before OD-21's acceptance. It was not live and needed no Stream variables.
  - **Result (26 September; Nathan ran it at high):** approve, so OD-21's acceptance is met. The manager applied its one documentation finding. Nit 2 is recorded as a correction, and the optional nit 3 is left as is. See the flake evidence record, "Exact-head review of the fix".
- **P06.1-C1, the I1 correction pass** (done; OD-29; [prompt](../ephemeral/2026-09-26-p06-1-c1-correction-prompt.md)).
  - One implementation session fixes the I1 review's findings 1 to 8 in the harness, and the nits within its scope, with a reason for any it leaves. It corrects the records that findings 4 and 8 name.
  - It makes no live run and no Stream call, so it needs no Stream variables and no Dev Manager read. The first live use of its fixes is in I2a.
  - Its own exact-head review follows. I2a starts only after that review is clean.
  - Finding 9 and finding 6's new setups belong to I2a.
  - **Result (26 September; Nathan ran it at extra high; branch `claude/youthful-pasteur-caokpc`, head `9e018c6`):** findings 1 to 8 and 15 of the 17 nits are fixed offline, each with a test that fails without its fix (51 reversals shown). Nits 14 and 17 are left as recorded limits. I1's claims are corrected in place, and the unit tests went from 49 to 142. The manager verified the branch and integrated it at `e85bba0`; see the evidence record, "P06.1-C1 corrections".
- **Review of C1** (done; OD-29; [prompt](../ephemeral/2026-09-26-p06-1-c1-review-prompt.md)). An offline exact-head review of the merge commit `e85bba0`. It needed no Stream variables and no Dev Manager read.
  - **Result (26 September; Nathan ran it at extra high):** approve. The I1 review's findings 1 to 8, and the 15 nits C1 claims, are confirmed fixed. Three should-fix findings and seven nits remain, and none changes a recorded result: an observed FAIL can be lost when a later step of its case is interrupted; T4-rest-unread can record HOLDS with a failed control; RT2 and RT3 record HOLDS on refusals that are not attributable. Two of them break the matrix quality rule and the third can hide an observed FAIL, so all ten are fixed before I2a spends live budget. See the evidence record, "Exact-head review of C1".
- **P06.1-C2, the second correction pass** (done; Nathan ran it at high; OD-29; [prompt](../ephemeral/2026-09-26-p06-1-c2-correction-prompt.md)).
  - One implementation session fixes the C1 review's findings 1 to 3 and nits 4 to 10, each with a test that fails without its fix, and brings the harness README into line.
  - It makes no live run and no Stream call, so it needs no Stream variables and no Dev Manager read.
  - Its own exact-head review follows, offline. I2a starts only after that review is clean.
  - **Result (26 September; branch `claude/lucid-einstein-79bqmd`, head `ba36311`, code head `f1c670b`):** the three findings and nits 4 to 10 are fixed offline, each with a test that fails without its fix. C2's own review sub-agent found four more problems, and C2 fixed those too. The unit tests went from 142 to 202, and the fix reversals from 51 to 99. The manager verified the branch and integrated it at `63e922f`; see the evidence record, "P06.1-C2 corrections" and the manager's verification under it.
  - **The manager's decisions on what C2 left open:** its rule for the undo of a client success after an interrupted control stands. In RT2 and RT3 a `feature` refusal gets "REFUSED (feature off; not a permission error)", not the HOLDS the C2 prompt directed (AM3-16); P06.1-C3 makes the change.
- **Review of C2** (done; OD-29; [prompt](../ephemeral/2026-09-26-p06-1-c2-review-prompt.md)). An offline exact-head review of the merge commit `63e922f`. It needed no Stream variables and no Dev Manager read.
  - **Result (26 September; Nathan ran it at extra high):** approve. The C1 review's ten items and C2's own four review points are confirmed fixed, and the reviewer agrees with both of the manager's decisions. Two should-fix findings and eight nits remain, and none changes a recorded result: a feature-gated case's observed FAIL becomes INCONCLUSIVE when its enabling request fails; a charge signal first met during the end of the run does not stop the cleanup. See the evidence record, "Exact-head review of C2".
- **P06.1-C3, the third correction pass** (done; Nathan ran it at high; OD-29; [prompt](../ephemeral/2026-09-26-p06-1-c3-correction-prompt.md)).
  - One offline implementation session makes the RT2 and RT3 change, fixes the C2 review's findings 1 and 2 and its nits 3 to 10, each with a test that fails without its fix, and brings the README into line.
  - RT2 and RT3: a `feature` refusal gets "REFUSED (feature off; not a permission error)". An `auth` or `permission` refusal gives HOLDS only when a control of the same request, by a member allowed to make it, succeeded (the brief's matrix quality rule): B's own `markRead` for RT3; none exists for RT2 while typing is off.
  - It needs no Stream variables and no Dev Manager read.
  - Its exact-head review follows, scoped to its change. After it, only a blocking finding, or a should-fix finding that could create a false HOLDS, lose an observed FAIL or send a request after a charge signal, delays I2a; other findings go into I2a's offline first step or the final delta review.
  - **Result (26 September; branch `claude/friendly-hypatia-ug6r52`, head `b40acd7`, code head `a5e2221`):** the RT2 and RT3 change, the two findings and the eight nits are fixed offline, each with a test that fails without its fix. C3's own review sub-agent found four more problems, and C3 fixed those too. A charge or limit signal is now recorded where its stop is raised, so no later exception can hide it from the end of the run. The unit tests went from 202 to 252, and the fix reversals from 99 to 147, each failing for its expected reason. The manager verified the branch, accepted C3's three decisions and integrated it at `8c1a8c0`; see the evidence record, "P06.1-C3 corrections" and the manager's verification under it.
- **Review of C3** (done; OD-29; [prompt](../ephemeral/2026-09-26-p06-1-c3-review-prompt.md)). An offline exact-head review of the merge commit `8c1a8c0`, scoped to C3's change. It needed no Stream variables and no Dev Manager read.
  - **Result (26 September; Nathan ran it at extra high):** approve. The RT2 and RT3 change, the C2 review's ten items and C3's own four review points are confirmed fixed, and the reviewer has no disagreement with the manager's decisions. Six nits remain, with no blocking or should-fix finding; only nit 1 could create a false HOLDS, in principle, and it is not new. The review also found a gap outside C3's change: a request a client session sends between commands is not checked for a charge or limit signal. Under the bound, nothing delays I2a; the nits and the gap go into its offline first step. See the evidence record, "Exact-head review of C3".
- **The Stream secret in cloud sessions** (OD-20, decided by OD-28). One `Glow app` environment stays. For each session that calls Stream, Nathan adds `STREAM_APP_ID`, `STREAM_API_KEY` and `STREAM_API_SECRET`, starts that one session, then deletes them; the prompt tells him when they are needed. They were present when the I1 review started, the first session that calls Stream under OD-28. App Manager 3's own container, started while they were set, still holds them; the manager never reads or uses them (AM3-17). So does the Dev Manager's container, which never reads or uses them either (AM3-19). Dev Manager 2's container, started at 16:16 UTC on 28 September in the `Glow app` environment, holds them too, so that environment held them then, after the last session that called Stream (I2b, 27 September); it never reads or uses them. App Manager 5 runs in Nathan's second Glow environment, `Glow App - No Stream`, and its container, started at 19:41 UTC on 28 September, holds none of them ([environment inventory](../operations/environment-inventory.md)). The economics discovery runs in Nathan's own browser, in neither. The secret is replaced at P06.1's close, which covers every container that held it. CI needs no Stream secret.

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

**Confirmed live** (DM-01 P4). The choice of the display rule as S15's answer rested on I1's own live evidence, so the exact-head review had to confirm S15 live. It did, on 25 September, and found no configuration that closes S15. So the display rule stands as S15's answer.

- **The live result.** Under the locked configuration, A's write got `200`, and B's ordinary channel query carried A's text inside the members list. B's members endpoint was refused (`403`, code 17). The control showed that B's reads could find the text.
- **One correction.** The realtime `member.updated` path is not established. The harness counted a local SDK event as B's, so it could not show which event carried the text (the review's finding 4). The channel query alone confirms S15. I2a maps the event types.
- **Nathan's principle** does not depend on the review: it is in force (DM-03 G4), and its exceptions are confirmed (OD-16).

See the evidence record, "Exact-head review of I1".

- **The design:** option 1 below, the display rule. The app never displays Stream user or member data. Every name, photo and profile field comes from Glow's API, and the app ignores member custom data and `member.updated` events.
- **The principle.** Nathan's second sentence reaches beyond S15. It is a product rule for every provider and every surface. The manager's working reading, which the Dev Manager approved with conditions (DM-02 B1):
  - users never see a sign that anything happens outside Glow;
  - no provider's name, branding, identifiers, error text, notifications or data reaches the user interface;
  - everything a user sees comes from Glow's API, in Glow's own wording.
- **Its scope** (DM-02 B1): Glow's in-app experience and every communication Glow sends: push, email, in-app errors, deep links and the links users share.
- **It binds server and operator consumers too:** Stream member or user custom data is never forwarded into exports, staff or WordPress views, push content or analytics.
- **The exceptions, confirmed by Nathan** (OD-16): legally required disclosures (privacy policies, store privacy labels, processor lists, and data-export contents where the law requires recipients), licence notices, and essential system screens. They are narrow and explicit, each with a named basis and a clear, usable screen. An optional product screen is not an exception because it is convenient. See ADR 0003, decision 4.
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
- The other member's client receives that text in its ordinary channel query and in a realtime `member.updated` event. (The I1 review later found the event path unproven; the channel query alone confirms S15. See "Confirmed live" above.)
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
3. **Guest reach (G2) and the poll vote (S10): yes.** I2a reruns them with a fresh budget, together with the other fixes not yet exercised live. The I1 review showed that both need new setups (finding 6); see I2a under "Sessions".
4. **Unguessable IDs: yes, a P06.2 requirement.** Stream user IDs are random and opaque, never derived from Glow's account IDs, names or emails, and never shown to other users. I2a records whether a refusal for an existing ID differs from one for an ID that does not exist.

### Reasoning levels

Each prompt's header gives its recommended level and, from the first prompt after OD-30 (26 September), its recommended model, Opus 5.5 or Fable 5.1. The readings and outcomes are kept only in the Notion page *TypeSafe effort scorer — Glow app usage log* (DM-01 P8), one row per session of this item.

## Risks and limits

- **Intermittent rendered-test failures** (three so far: a form submit that does not advance) can turn P06.1's CI red. Nathan directed their diagnosis now, inside P06.1 (OD-21); see "Sessions". A passing rerun does not resolve them.
- **S15** is decided: the display rule. Its residual risk stays recorded under "S15: decided", and P06.2 must enforce the rule with a test.
- **WebSocket:** verified by I1. The environment's proxy passes Stream's WebSocket: connect, events, disconnect and reconnect.
- **The dashboard side effect,** which Nathan accepted: the admin role has no grants in the default types or `glow-match`. Restoring the recorded baseline returns the default types' grants.
- **Silent passes:** a bypass test can pass for the wrong reason, for example a malformed request that fails for itself. The matrix quality rule answers this, and the exact-head review checks it.
- **Billing:** the Free Chat plan's limits are far above the guardrails, but Stream's general policy is automatic overage billing and no payment method is on file. Before any real traffic, Nathan settles the billing arrangement (A04).
- **Sandbox scope:** results cover the development application, its plan and synthetic users at the time of the run. Real persistence, concurrency and restore behavior stay with P11. Production credentials and launch pricing are separate.
- **Secret exposure:** every command in a `Glow app` session can read the development secret. If exposure is ever suspected, rotating it in the Stream dashboard and the environment settings is cheap.
