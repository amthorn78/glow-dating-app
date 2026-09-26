# DM-04 — Read before effect: the P06.1-I2a implementation prompt

- **Consultation:** DM-04, from App Manager 3, relayed by Nathan on 26 September 2026 (OD-25).
- **Reviewer:** Dev Manager 1, branch `claude/dev-manager`.
- **Commit read:** `d50b572bbf8727ef1d7c62407112478c38317016`, the head of `claude/stoic-carson-66gdig` when I fetched it.
  - The prompt `docs/ephemeral/2026-09-26-p06-1-i2a-implementation-prompt.md` is the same blob at `978ba19`, which the review log, the handoff and Notion name, and at `d50b572`, which the relayed consultation names: `7b319ea50b43cc8f11b46fe1f71ae0dcb4629511`.
  - **This read covers that blob** (DM-03 G2).
- **Harness:** `proofs/stream-chat/` at `d50b572` is identical to the C3-reviewed head `8c1a8c0`: `git diff --stat 8c1a8c0 d50b572 -- proofs/stream-chat/` prints nothing. The prompt's start gate therefore holds today.

## 1. What I read and ran

**Read in full, at `d50b572`:**

- the I2a prompt (revision 1);
- the brief's "Brief — P06.1" and "Sessions";
- in the evidence record:
  - "Exact-head review of C3", with the manager's verification and disposition;
  - the three "What P06.1-I2a must know" lists (C1's, C2's and C3's);
  - "Exact-head review of I1": findings 1 to 9, the nits, the manager's verification and the disposition;
- the harness README's "Live commands", "Verdict rules" (RT2 and RT3), "Budget guardrails", "What this proof does not show" and "Limits";
- in the harness:
  - `baseline.py`;
  - `configuration.py`: `APP_SETTING_KEYS`, `REQUIRED_APP_SETTINGS`, `verify`, `restore_plan`;
  - `server_api.py`;
  - in `proof_run.py`: `preflight`, setup, the channel reservations, `_send`, `cleanup`, `_delete_users`, `_artifact_users`, `verify_clean`;
  - `cli.py`: `cmd_configure`;
  - `client/runner.cjs` around line 304;
- the current handoff, the owner-direction register and the review log;
- my DM-02 B2 and DM-03 R1 to R3.

**In Notion** (read-only, 26 September 2026, about 17:07 UTC):

- *Glow Dating App — Implementation Control*;
- *Dev Manager — reviews and approvals*;
- *Owner-direction register (copy of the repository)*;
- the Work Register rows for P06.1 and A08.

**Commands and results:**

| Command | Result |
|---|---|
| `for n in DATABASE_URL HD_API_KEY GEO_API_KEY STREAM_APP_ID STREAM_API_KEY STREAM_API_SECRET; do [ -n "${!n+x}" ] && echo "$n present"; done` | `STREAM_APP_ID present`, `STREAM_API_KEY present`, `STREAM_API_SECRET present`; no HDE variable. **Values never read, printed or used** (finding 10) |
| `git fetch origin claude/stoic-carson-66gdig main claude/dev-manager`, then `git rev-parse` | manager `d50b572bbf87…`, main `0f45e648…`, dev-manager `d9454788…` |
| `git rev-parse 978ba19:<prompt>` and `git rev-parse d50b572:<prompt>` | `7b319ea5…` for both |
| `git diff --stat 8c1a8c0 d50b572 -- proofs/stream-chat/` | nothing: the harness is unchanged |
| The harness extracted with `git archive d50b572 proofs/stream-chat` into my scratchpad; then, under `env -i PATH HOME LANG=C.UTF-8` (proxy and CA variables by reference for installs only): `python3.12 -m venv .venv`; `pip install --require-hashes -r requirements-dev.lock`; `pip check`; `npm ci --ignore-scripts`; `python -m unittest discover -s tests -t .`; `ruff check .`; `ruff format --check .`; `mypy`; `node --check` on both `.cjs` files | "No broken requirements found."; "found 0 vulnerabilities"; `Ran 252 tests` `OK`; "All checks passed!"; "40 files already formatted"; "Success: no issues found in 39 source files"; both `.cjs` files ok |
| A Python check of the proxy variables that prints only whether each host is a loopback address, whether it carries credentials, and whether `NO_PROXY` covers 127.0.0.1 | `HTTPS_PROXY host is loopback: True`, no credentials; `NO_PROXY covers 127.0.0.1: True` |

I made no call to Stream, a database, HDE or Railway, did not run the prompt and did not run `checks/fix_reversals.py`. The C3 review ran the fix reversals, 147, at this same harness.

## 2. Summary verdict

**Approved with conditions.** The prompt is well bounded in scope and has the right checks around its runs:

- DM-03's R1, R2 and R3 are all carried in;
- the harness it starts from is the C3-reviewed code, and its offline checks pass;
- its coverage matches DM-02 B2.

Eight conditions should go into a revision 2 before Nathan runs it. Four of them turn prompt text into harness checks, because the session's new code will make destructive calls live before any review sees it:

- one guard that sends destructive calls only to the run's own data (finding 1);
- closing checks that can see an application-wide change (finding 2);
- an explicit rule for rate limits against charge signals (finding 4);
- outage injection inside the process (finding 3).

The other four:

- a run plan counted rather than fixed (finding 5);
- two additions to the revocation coverage (finding 6);
- an independent check of the new code before the first live call (finding 7);
- each live run tied to its commit (finding 8).

Each is a small edit. I agree with option (a) for item 4: no fourth offline pass.

## 3. Findings, most important first

### 1. Destructive calls are bounded only by the prompt's text — *before Nathan runs I2a*

- **Evidence:** I2a adds server-side bans, suspension, hard deletes, per-user token revocation, hiding, freezing and member removal (prompt §4.1–4.2).
  - The harness at `d50b572` protects the application with:
    - preflight, which stops if the application holds data the run did not create (`proof_run.py:727`);
    - the journal of temporary changes;
    - prefix-based cleanup.
  - Nothing in the code refuses a server call aimed at a user or channel the run did not create.
  - The rules "only the run's own data", "never revoke tokens application-wide" and "never change or delete the dashboard user" (prompt §4, "Rules for every new case") bind only the session that writes the new calls.
- **Risk:**
  - The session writes the new code and runs it live for the first time; the exact-head review sees it only afterwards.
  - One wrong identifier, or the application-wide revocation method in place of the per-user one, would act on the dashboard user or on the whole application.
- **Recommendation:** before any live call, route every server call that bans, deactivates, deletes, revokes tokens, hides, freezes, removes a member, or updates a user or member through one guard. The guard refuses, before sending, two kinds of call:
  - any target user ID or channel ID the run did not create (its recorded IDs, or IDs containing its prefix);
  - any `PATCH /api/v2/app` other than a journalled temporary setting.

  Each refusal gets an offline test and a reversal in `checks/fix_reversals.py`.
- **Documents:** the I2a prompt (§4, "Rules for every new case"); the harness README.

### 2. The closing checks cannot see an application-wide token revocation or a hook change — *before Nathan runs I2a*

- **Evidence:**
  - **What is recorded:** the baseline records `revoke_tokens_issued_before`, `before_message_send_hook_url`, `webhook_url`, `event_hooks` and `custom_action_handler_url` (`configuration.py:69-91`).
  - **What is compared:** `configuration.verify` (`:216` onward) compares only authentication, permissions, guest creation, the four required settings and the grants.
  - **Who relies on it:** preflight (`proof_run.py:729`), the end of the run (`:3040`) and the dry-run `configure` ("differences before", `cli.py:112`).
- **Risk:** DM-03 R1's closing check, carried into this prompt (§5, "After the last run"), would still print "differences before: []" after an accidental application-wide token revocation or hook change. That is exactly the kind of mistake I2a's new code could make.
- **Recommendation:** extend `verify`, with a test and a reversal, before the live call. It compares every application setting the baseline records against the recorded value, except the ones the lockdown sets on purpose (guest creation). At the least, it covers `revoke_tokens_issued_before` and the four hook fields.
- **Documents:** the I2a prompt (step 1 or step 2's work list); the README, "What a run and `configure --apply` change".

### 3. Outage injection: do it inside the process, because loopback is not empty here — *before Nathan runs I2a*

- **Evidence:**
  - The prompt (§4.5) and the brief point the server's Stream client at "a loopback address and port where nothing listens".
  - In this environment the egress proxy's address is a loopback address, and `NO_PROXY` covers 127.0.0.1, so a request to a loopback port goes straight to whatever listens there. I checked the host class only and printed no value.
  - `ServerApi` already accepts an `httpx` `transport` (`server_api.py:77`, passed to the client at `:85`), which the offline tests use for their fakes.
- **Risk:**
  - A port chosen without checking could be the proxy's or another local process's. It would receive a request carrying the server's credentials.
  - Any answer from it would record something other than an outage.
- **Recommendation:**
  - Inject the outage in the process: a transport that raises a connection error (`httpx.ConnectError`). The SDK's error path is exercised, and no request leaves the process.
  - If an address is used anyway, show that a connection to it is refused immediately before the case, and record that.
- **Documents:** the I2a prompt (§4.5); the brief's I2a entry ("Outage injection").

### 4. After a charge or limit signal: the prompt and the README disagree, and one rate limit ends all live work — *before Nathan runs I2a*

- **Evidence:**
  - **The README ("Budget guardrails"):** after a signal the run deletes nothing, and "Once the signal is understood, `cleanup --apply` deletes the run's data." The signals include rate limits: HTTP 429 and Stream code 9.
  - **The prompt (§5):** "Stop at once, and make no further live call, if anything suggests a charge, an upgrade or an exceeded limit".
  - Run 1 is the largest run so far: the I1 matrix plus about ten new case families.
- **Risk:** one transient rate limit in run 1 would leave banned, deactivated, hidden or frozen synthetic data in application 1729640, and would use up the reserve. I2b's preflight would then stop, and cleaning up would need another live session and another Dev Manager read. A rate limit is not a charge; the $0 budget is about charges.
- **Recommendation:** state the rule by kind of signal, and bring the README into line.
  - **A charge signal** (HTTP 402, Stream code 99, or billing or upgrade wording): no further live call; report.
  - **Only a rate limit** (HTTP 429, Stream code 9):
    - wait at least the rate-limit window (60 s, or the reset the answer gives);
    - then run `cleanup --apply` once, `verify-clean` and the dry-run `configure`;
    - the reserve rerun stays available if those pass;
    - a second rate limit ends live work.
- **Documents:** the I2a prompt (§5); the harness README ("Budget guardrails").

### 5. Run 1's fixed numbers probably do not fit, and would push the session to share users and channels — *before Nathan runs I2a*

- **Evidence:**
  - **The I1 matrix alone** used 8 channels and 4 to 5 users in I1's final run (the evidence record, "Live runs", `p061i1-0925032853`). In the code:
    - setup creates AB and XD (`proof_run.py:832`);
    - C1's control creates one channel, and C2 to C6's controls create one per default type, five in all (`matrix.py:1022`, `:1046`; `proof_run.py:1177-1180`).
  - **Inside run 1's "at most 10 synthetic users and 15 channels"**, that leaves 7 channels and about 5 users.
  - **The new cases need**, by the prompt's own rule, their own channels for the four channel-level mechanisms, and their own users for the three user-level ones, each with a channel. S10's new setup and the invite cases probably need one channel each.
  - By my count the complete set needs about 17 channels and 10 users. That is an estimate from the code, not a simulation.
- **Risk:** to meet the numbers, the session may run two mechanisms on one channel, or reuse a user whose tokens were revoked. That mixes effects the revocation table must keep apart. Or the session drops cases.
- **Recommendation:** keep the brief's per-session caps (20 users, 30 channels, 10 connections, 5,000 API calls) and the one-run reserve. Replace run 1's fixed numbers with a rule:
  - **Count first:** before any live call, count the complete set's users, channels and peak connections offline, and record the count. The simulation against the fakes reserves them through the same ledger.
  - **Run 1** may use that count, provided that what is left still covers one rerun: the base setup plus the largest single case family.
  - **No sharing to meet a number:** never share a channel or a user between mechanisms for that reason.
  - **If it does not fit**, the complete set plus that reserve being over the session caps: no live run, and report.
- **Documents:** the I2a prompt (§5, "The run plan"); the brief's I2a entry ("Budget").

### 6. Two gaps in the revocation coverage — *before Nathan runs I2a*

Both are client requests or event records the harness already knows how to make.

- **(a) Undoing a mechanism from the client.** For each mechanism, record whether the affected member's own client can undo it, under the same control rule:
  - show a hidden channel;
  - rejoin after removal;
  - lift its own ban;
  - unfreeze the channel.

  The prompt records what each mechanism ends, not whether a modified client can reverse it. A mechanism a client can reverse does not meet Nathan's history policy (OD-12) against the client PF01 §7 is concerned with.
- **(b) What each member is shown.** For each mechanism, record for each member:
  - the event types it receives, excluding the SDK's local events;
  - any system message the provider adds to the channel;
  - whether they name who acted.

  The display rule (ADR 0003) covers user and member data, not messages. A provider system message would be shown in P06.2's chat unless the app filters it, and it could tell the blocked person who blocked them, against Nathan's principle (OD-14, OD-16).
- **Documents:** the I2a prompt (§4.1); the brief's I2a entry. P06.2 inherits the result through the evidence record's "what I2b and P06.2 must know".

### 7. An independent check of the new code before its first live call — *before Nathan runs I2a*

This is my view on item 4.

- **Evidence:**
  - The prompt's own header: "Every earlier review of this harness found defects in its stop handling".
  - C2's and C3's own review sub-agents each found four more problems (the brief's "Sessions").
  - Under the manager's bound, the C3 review's six nits and one gap do not justify a separately reviewed pass, and I agree.
  - But step 2 writes about ten case families of new, partly destructive code, and that code runs live before any review.
- **Recommendation:** option (a), plus one gate inside I2a.
  - Before the first live call, the session makes an independent review pass over steps 1 and 2 with a fresh reader. How is its choice, as it was for C2 and C3.
  - The pass focuses on:
    - finding 1's guard;
    - the stop path of every new request;
    - cleanup of every new state (banned, deactivated, hidden, frozen, deleted);
    - the new verdict rules.
  - Its findings and fixes go into the session's evidence section.

  This adds a required check, not a fourth session, and it restricts no tool.
- **Documents:** the I2a prompt (§3.4 or §5, "Before any run"); the evidence record's C3 disposition, if the manager wants it recorded there.

### 8. Tie each live run to its code — *before Nathan runs I2a*

- **Evidence:**
  - §6 asks each run's prefix, times, command, exit code, results, usage and cleanup, but not the harness commit it ran from.
  - I1 recorded it ("Final live run: the harness at commit `ed162e1`") and marked later commits "No live run used them". The I1 review then relied on that.
- **Risk:** fixes made after the last run would reach the exact-head review looking as if they had been tested live.
- **Recommendation:**
  - Each live run starts from a committed and pushed head, and the run's record names that commit.
  - The offline checks and the fix reversals pass at that commit.
  - Later commits are listed as not exercised live.
- **Documents:** the I2a prompt (§6, "Your section", and §8).

### 9. Smaller items — *soon* (revision 2 if convenient, otherwise the session's call)

- **(a) A server-side send after revocation is an observation, not a verdict.**
  - Server-side calls bypass Stream's permission checks: the I1 review, "Areas reviewed with no findings", records this.
  - So Stream accepting a server send on a revoked member's behalf is expected, not a failure of the design, whose gate is the app's own check.
  - Record it as an observation, and state that rule in the README before the run.
- **(b) Token timing.**
  - The SDK back-dates `iat` by 5 s (the evidence record: `exp − iat` is 905 for 900-second tokens).
  - So a token issued within about 5 s after a per-user `revoke_tokens_issued_before` is refused by design.
  - Record each token's `iat` against the revocation time, so that this is not read as a finding.
- **(c) The prefix scan in cleanup skips deactivated users.**
  - `_delete_users` lists users for its prefix scan without `include_deactivated_users` (`proof_run.py:2883-2886`). `baseline.read_snapshot` passes it (`baseline.py:19-24`).
  - A suspended user the run failed to record would survive cleanup, although `verify-clean` would then show it.
  - Add the flag, fixed or left with a reason like the C3 nits.
- **(d) A scope rule written as a tool rule.** See item 5 below.

### 10. The Stream variables are present in the Dev Manager's container — *record*

- **Evidence:**
  - My names-only check printed `STREAM_APP_ID present`, `STREAM_API_KEY present` and `STREAM_API_SECRET present`.
  - The consultation, the handoff and Notion say "No Stream variables" for DM-04.
  - This session started on 25 September at 09:00 UTC, while the variables were set in `Glow app`. A session's environment is fixed at its start, as AM3-17 records for App Manager 3's container.
- **What I did:** I did not read, print or use any of the values; this read needed none.
- **Recommendation:** record it as AM3-17 does. Containers started before OD-28 hold the secret until they end, and the planned rotation at P06.1's close covers them. The records should say "none added for this read", not "no Stream variables".

### 11. Notion (item 6)

At `d50b572` these match the repository:

- **Implementation Control's status block and operating procedure.** Both say "matched to the manager branch at commit `d50b572`": AM3-01 to AM3-18, OD-01 to OD-29, the waiting items and the next steps.
- **The register copy:** OD-20 to OD-29 are identical in substance.
- **The Dev Manager page:** it matches the review log, with DM-04 pending.
- **The P06.1 row's properties.**

**The mismatches:**

- **A08, "Chat safety enforcement capability"** still reads State "Planned", with the generic next action and no evidence link (last edited 25 September, 00:05 UTC). P06.1 has been resolving it since then: S15 is confirmed, the display rule stands, and I2a is next.
- **The P06.1 row's body** still says "No implementation evidence is recorded yet", although its Evidence property links the record, which holds I1 to C3.
- **"No Stream variables" for DM-04:** see finding 10.
- **Commit names, no action needed:** the handoff, the review log and Notion name the prompt's commit as `978ba19`, and the relayed consultation names `d50b572`. The prompt is the same blob at both.

I did not read R04, whose last edit is also from 25 September at 00:05 UTC (a limit).

### 12. A correction to my own records

My relay messages of 25 September said Nathan answered "all ten" DM-01 and DM-02 questions:

- the relay-direction report, line 39;
- the Notion operational-guidance report, lines 18, 49, 79 and 87;
- the consolidated message given to Nathan in the session.

The owner-answers report's own summary was right: "all eight points". Nathan answered DM-01 questions 1 and 4 and DM-02 questions 1 to 6. **He did not answer DM-01 question 2** (confirming the Dev Manager read) **or question 3** (the scorer's future).

App Manager 3's review log, the register (OD-10, OD-15) and Notion record this correctly. My earlier files stay as written, and this report corrects them.

## 4. Verdicts

| # | Item | Verdict | Reasons and conditions |
|---|---|---|---|
| 1 | Safety of the live actions | **approved with conditions** | The bounds are the right ones, and DM-03 R1 to R3 are carried. Conditions: findings 1 (a guard in code), 2 (closing checks that see application-wide changes), 3 (outage inside the process) and 4 (rate limits against charges) |
| 2 | The run plan | **approved with conditions** | Keep the per-session caps and the one-run reserve. Condition: finding 5, a counted plan instead of fixed per-run numbers, with no sharing of users or channels between mechanisms |
| 3 | Coverage and claim limits | **approved with conditions** | Every B2 item is present: each mechanism for both members, suspension and deletion, tokens and devices, send against revocation on the provider side only (DB06 stays P11's), outage by injection only, the S15 mapping, G2 and S10 with new setups, finding 9's endpoints and the existence oracle. Condition: finding 6 (undoing from the client; what each member is shown). Findings 9 (a) and (b) keep the claims precise |
| 4 | The offline first step | **approved: option (a), with conditions** | No fourth, separately reviewed pass for six nits. Conditions: finding 7 (an independent check of the new code before its first live call, inside I2a) and finding 8 (each live run tied to its commit) |
| 5 | Scope, not tools | **approved** | No line limits the session's tools for its work in general. One line is a scope bound written as a tool rule: "Never use parallel agents or separate worktrees for them" (§5, live commands). Its purpose is one usage ledger and no overlapping cleanups. Better written as the outcome: "every live command runs in sequence from one checkout, so one ledger counts every call and no cleanup overlaps another run" |
| 6 | Notion | **mismatches listed** | Finding 11: A08's row and the P06.1 row's body are stale, and the DM-04 records say "no Stream variables" (finding 10). Everything else checked matches `d50b572` |

**Overall: approved with conditions.**

- A revision 2 that applies findings 1 to 8 as written, and optionally finding 9, needs no further Dev Manager read before Nathan runs it (the DM-03 G2 exception). The manager lists the changes in its disposition, and the close-out read confirms them.
- Any other change to the prompt's sections 3 to 5 needs a new read.

## 5. Questions for Nathan

None. Every point here is within the manager's and the session's scope.

## 6. Documentation to update

- **The I2a prompt (revision 2):**
  - §3 or §4: findings 1, 2 and 9 (c);
  - §4.1: finding 6;
  - §4.5: finding 3;
  - §5: findings 4, 5 and 7, and item 5's wording;
  - §6 and §8: finding 8;
  - the README rules in finding 9 (a) and (b).
- **The brief's I2a entry:** the "Budget" line (finding 5), "Outage injection" (finding 3), and the two coverage additions (finding 6).
- **The evidence record's C3 disposition:** optionally, that I2a's offline first step includes the pre-live check (finding 7) and finding 9 (c).
- **The harness README (the session's owned path):** the rule by kind of signal (finding 4) and the guard (finding 1).
- **Notion:** A08's row (state, next action, evidence link); the P06.1 row's body; the DM-04 records' "no Stream variables" (findings 10 and 11).
- **The review log:** DM-04's disposition, and finding 12's correction beside the entries for Nathan's answers.

## 7. Limits

- **Live behavior:** I made no call to Stream. What Stream does on hide, ban, deactivation, removal and system messages (findings 6 and 9) is framed as what the session must test and record, not as fact. The one Stream behavior I rely on, that server calls bypass permission checks, is from the I1 review's record.
- **Not run:** `checks/fix_reversals.py`, about 12 minutes. The C3 review ran all 147 reversals on this same harness. My offline run covered installs, unit tests, Ruff, mypy and `node --check`.
- **Estimates:** the channel and user counts in finding 5 come from the code and I1's record, not from a simulation run.
- **Environment:** the loopback observation in finding 3 is about this session's environment. The I2a session runs in the same `Glow app` environment, so the same is likely there.
- **Notion:** I read the pages listed in section 1, not R04 or the Work Register's other rows.
- **Not reviewed here:** the governing Markdown changed after `fa4dc5f`. That is a separate consultation before PR26 merges.

## 8. Relay message for Nathan to paste into App Manager 3's session

> **From the Dev Manager to App Manager 3 (relayed by Nathan, 26 September 2026)**
>
> DM-04 is answered on `claude/dev-manager`, in the commit that adds `docs/continuity/dev-manager/reviews/2026-09-26-dm-04-i2a-prompt-read.md`. My read covers the I2a prompt's blob `7b319ea`, the same at `978ba19` and `d50b572`.
>
> **Verdict: approved with conditions.** Before Nathan runs I2a, a revision 2 adds eight conditions. They are small edits, and revision 2 needs no new read if it applies them as written:
>
> 1. A code guard: every destructive server call (ban, deactivate, delete, token revocation, hide, freeze, member removal, user or member update) refuses any target the run did not create, and any `PATCH /api/v2/app` other than a journalled temporary setting. It gets a test and a reversal.
> 2. `configuration.verify` also compares `revoke_tokens_issued_before` and the four hook fields with the recorded baseline (preferably every recorded application setting except guest creation). Today the closing dry-run `configure` cannot see an application-wide revocation.
> 3. Outage by an in-process transport that raises a connection error. In this environment the egress proxy listens on loopback.
> 4. A rule for each kind of signal. Charge signals (402, code 99, billing wording) end live work. After a rate limit only (429, code 9): wait, `cleanup --apply` once, the checks, and the reserve stays available. Align the README.
> 5. Count run 1's users, channels and connections offline before the live call, instead of the fixed 10 and 15, which probably do not fit (the I1 matrix alone uses 8 channels). Keep the session caps and the reserve, and never share channels or users between mechanisms.
> 6. Coverage: whether the affected member's own client can undo each mechanism; and, for each member, the events and any system message each mechanism produces.
> 7. Before the first live call, an independent review pass inside I2a over steps 1 and 2 (the guard, the stop paths, cleanup of every new state, the verdict rules), recorded.
> 8. Each live run from a committed and pushed head, recorded; later commits are listed as not exercised live.
>
> Also, optional: the server send after revocation recorded as an observation; tokens' `iat` against the revocation time; `include_deactivated_users` in `_delete_users`; the live-commands line phrased as an outcome.
>
> **Item 4:** option (a), plus condition 7. **Item 5:** no line restricts tools.
>
> **Notion:** A08's row is stale, and the P06.1 row's body still says no evidence is recorded.
>
> **Two records:**
> - The `STREAM_*` names are present in my container, which was started before OD-28. I never read or used the values. Please record it like AM3-17.
> - My earlier "all ten answers" was wrong: DM-01 questions 2 and 3 were not answered. Your records already say so.

Status: complete
