# DM-17 — Stream's additions, the correction pass B2-C1, and B2's open dispositions

- **Consultation:** DM-17, revision 1, from App Manager 6, relayed by Nathan (OD-25).
- **Reviewer:** Dev Manager 2, `session_015DxVkL8PXn2YaauE6RdSWN`, branch `claude/dev-manager`.
- **Commit read:** `5ae3c23899c6d884fb3c23658c62a57ffa42c523` of `claude/magical-wozniak-yfmmx2`. The code is read at `957dccb`. **This read covers `5ae3c23`** (DM-03 G2).
- **The live head when I fetched** was `d9f6c1e`, two commits later (`9371e24`, `d9f6c1e`). They record OD-43 in the register, the manager workflow's step 3, the environment inventory and the brief's "Sessions". They are governing Markdown this read does not cover (item 7).
- **Environment (names only):** `STREAM_APP_ID`, `STREAM_API_KEY` and `STREAM_API_SECRET` are present, never read or used. No HDE name is present. I called no provider, database, HDE or Railway, and ran no code.

## 1. What I read

**At `5ae3c23`:**

- The evidence record's "Stage B2", whole, including:
  - "Items 1 to 8";
  - "The recorded choices";
  - "The new resolved packages";
  - "The live run";
  - "Checks";
  - "Deviations, findings and limits";
  - "What the exact-head review must know".
- "Manager verification of Stage B2".
- The brief's diff `2542a06..5ae3c23`, whole.
- The B2-C1 prompt, revision 1, all 136 lines.
- The governing diff `2f62b1e..5ae3c23` over `AGENTS.md`, `CLAUDE.md`, `docs/pf-canon`, the manager workflow, the charter and the CI policy.
- ADR 0003's "Conditions" and "Revisit when".
- The architecture document's sections 3 to 5.
- OD-34, OD-42 and AM6-03.

**At `957dccb`:**

- `services/api/glow_domain/chat_provider_stream.py`: the error mapping, the boundary and the six operations;
- `services/api/pyproject.toml`'s mypy overrides;
- `glow_chat/delivery.py`, lines 425 to 470 (the call and settle);
- `glow_domain/chat_provider.py`'s `error_code`;
- in `proofs/stream-chat/`:
  - `products.py`: `PRODUCTS_BASELINE`, `CLIENT_ROLES`, `verify`, `baseline_differences` and `baseline_record`;
  - `configuration.py`'s `verify`;
  - `cli.py`'s `cmd_configure` and `_configure_products`;
  - `guard.py`'s `ConfigureScope`;
  - the committed `baseline/video-feeds-1729640-2026-09-27.json`, whose grant counts I read per scope;
  - the application baseline's keys.

**Notion, read-only, 23 October:**

- *Implementation Control*, including its operating procedure;
- the Work Register's P06.2 row;
- *Dev Manager — reviews and approvals*;
- the uses table's rows for Stage B2 (revisions 1 and 2) and B2-C1, revision 1.

## 2. Summary verdict

| Item | Verdict |
|---|---|
| 1 D1 to D4 | **Approved with one condition, on D3:** the new products baseline keeps the 27 September record's client-role grants, or point ii's own check stops the session on every known scope |
| 2 Points i to iv | **Approved with conditions 2.1 to 2.4.** On iv: **the general `configure --apply`**, with a full before-and-after snapshot comparison for each apply, since that apply runs outside the guard |
| 3 B2-C1's prompt: authority and safety | **Approved with conditions 3.1 to 3.4.** Nothing too wide. Revision 1 does not run as it is: its baseline check would stop it |
| 4 B2's three changes outside its words | **Approved, all three.** The creator, with the exact-head review's confirmation; a note for P11 |
| 5 B2's findings | **Approved, with one condition:** the API's development lock is aligned with the harness's before the live rows. Two items confirmed from the code here |
| 6 Production, and the D8 question | **The P11 drift check: approved.** **The D8 trigger is met:** by D1, D2 and D4, not only D1. **Referred to Nathan** in OD-32's form, after B2-C1's live rows and before Stage C's prompt. It does not block B2-C1 |
| 7 The governing changes since DM-16 | **Confirmed:** DM-16's words as written. `9371e24` and `d9f6c1e` are not covered |
| 8 Notion | **Matches**, apart from two uses-table rows |

A revision 2 of the B2-C1 prompt and the brief that applies sections 3.1 to 3.5's conditions as written needs no further read (G2). Item 6's question is Nathan's; nothing else is.

## 3. Findings

### Item 1 — The disposition of D1 to D4: approved, with one condition on D3

**D1, remove `schedule-message` from `glow-match`'s `channel_member`: approved.** It is not cosmetic. It gives each member of a match a client write into the match channel outside Glow's send path. That path's block, pause, consent and moderation checks (D5) never see a scheduled message, and whether one scheduled before a removal still fires after it is not known. The target stays `read-channel` alone.

**D2, empty the `agent` call type's `user` and `guest` grants: approved.** `user` holds `create-call`, `join-call`, `send-audio`, `send-video` and `send-event` there. A token Glow issues for chat could start a call with the other member: the path the architecture document's sections 3 and 6 close by the lockdown.

**D4, lock the chat type `agent`: approved**, with point i so the next added type is caught. `user` holds 25 grants in a type the target never inspected. That is a client surface beside the match channel, outside its removal.

**D3, re-baseline: approved, with this condition.**

- **The problem.** The committed `video-feeds-1729640-2026-09-27.json` was recorded *before* the lockdown. It holds the client roles' original grants for the four call types and five feed visibilities (for example `audio_room` `user` 29, `anonymous` 2; `public` `user` 26, `guest` 8). That is what makes it the record of "every grant removed" (architecture section 5).
- Today's snapshot holds those client roles empty. A new file written by `record-products-baseline` from today's snapshot would differ from the old one at every client role of every known scope, not only at `agent` and the four `lifecycle` sections.
- Point ii's own check ("the diff … must be `agent` and `lifecycle` … and nothing else; otherwise stop") would then stop the session. If the check were loosened instead, the file would lose its meaning.
- **1.1 The condition.** The new baseline takes, for every scope the 27 September file holds, the client roles' grants from that file unchanged; everything else comes from the fresh snapshot. `agent`'s client grants are recorded as read today, before its lockdown. Then the file still means "each scope's grants before the lockdown", and point ii's diff check holds as written.
  - `verify` ignores client roles in `baseline_differences`, so this changes no verification.
  - An offline test shows the merge on the fakes.
  - The README and the architecture document's "Restoring" sentence name the new file.

### Item 2 — B2-C1's design points: approved with conditions

**i. Generic channel-type coverage: approved.** It is the right shape: every type except `glow-match` holds no grant, the five named types must still exist, `configure` empties any type it sees, and `restore` leaves alone a type the pre-proof record lacks.

- **2.1 One addition.** The listing point i makes for `glow-match`'s unnamed fields is also made for the application settings: every key the 25 September record and the target do not name, with its value. A key that turns on a content feature or a client write stops the session before item 4.2. Stream added a permission to an existing role. It can add an application setting the same way, and `verify`'s application check compares only what the record names.

**ii. The products baseline:** as item 1's 1.1.

- **2.2** B2-C1's owned paths add whatever 1.1 needs: `products.py`'s record function, or `cli.py`'s `record-products-baseline`. The 27 September file stays byte-identical and is kept.

**iii. The live order: approved,** with one addition, which is what makes iv safe:

- **2.3 A full comparison around each apply.** Before and after each of the two applies, the session takes a full snapshot and compares every field of:
  - the application settings and `.app` grants;
  - every chat channel type;
  - every call type and feed visibility.

  It leaves aside only volatile values such as `updated_at`, each of them named. The only changes allowed are D1 and D4 for the chat apply, and D2 for the products apply. Anything else is reported first, before any further command, and there is no second apply and no restore.
- `verify` checks what the targets name; this check sees what they do not.

**iv. The general `configure --apply`: approved,** over a differential chat apply, with 2.3.

- **2.4 Know what it is.** `cmd_configure`'s own comment says the general apply re-sends the application `PATCH`, the default types and `glow-match` **outside the guard**, as on 25 September. That is acceptable for one reviewed command with:
  - the dry-run check of point iii (each planned request re-sends a held value or corrects D1 or D4, shown from the snapshot);
  - 2.3's comparison after it.

  Writing a differential chat apply now would add new apply code to a live correction pass, which is a larger risk than re-sending reviewed values.
- **For production**, a differential chat apply under a configure-scope guard, as the products have, is the better form. P11 carries it with the drift check (item 6).

### Item 3 — B2-C1's prompt, revision 1: approved with conditions

The authority is right and no wider than the work:

- the three names in `Glow app`, read only by the harness's loader;
- reads of Chat, Video and Feeds;
- one `configure --apply`;
- one `configure --products video,feeds --apply`, planned as exactly one `PUT /api/v2/video/calltypes/agent`;
- no `restore --apply`, no second apply, no dependency change;
- stops on any extra difference, any wrong re-read, and any charge or limit signal;
- then B2's item 7.2, with DM-16's rerun and blocking rules.

The conditions:

- **3.1 Item 4.2 as 1.1.** As written, item 4.2's diff check stops the session predictably (item 1). Revision 2 states the merged record and the diff it must show. With that, the stop rule stays as written.
- **3.2 Items 4.3 and 4.4 gain 2.3's full comparison**, and item 4.1 gains 2.1's application-settings listing. Item 4.3 says that the general apply runs outside the guard, and why that is accepted (2.4).
- **3.3 The lock alignment (item 5, condition 5.1) is an offline item before item 3,** so the live rows run under the lock the API will merge. The owned paths add, for it alone:
  - `services/api/requirements-dev.lock`;
  - `services/api/dependency-inventory.json`;
  - `services/api/tests/test_dependency_pins.py`.

  The "never" line on dependencies becomes "add no dependency; change no version except item 5.1's alignment".
- **3.4 A half-applied state is reported, not repaired.** If an apply fails part-way, the session stops with its record, as written. The report then says which requests were applied and gives the after-snapshot's comparison. The development application's state is then a new decision, not this session's.

### Item 4 — B2's three changes outside its prompt's words: approved

- **The creator** (`created_by_id` = the first member): accepted as a precision of DM-16 4.2.
  - Stream's server-side get-or-create needs a creator when no user token is sent. The value is an identifier of a member already in the request.
  - The exact-head review confirms, as the manager proposes, that `glow-match` grants no owner-scoped permission to any role, so ownership confers nothing today.
  - **For P11, recorded, not a condition:** ownership makes one member the target of any owner-scoped grant Stream might add to `glow-match`, as it added `schedule-message`. A server-only creator identity, provisioned once and never issued a token, removes that asymmetry. P11 weighs it with the drift check.
- **`pyproject.toml`'s override:** accepted. It is scoped to `getstream` and `getstream.*` only (`pyproject.toml:20-22`) and changes no strictness elsewhere.
- **The API README's paragraph:** accepted.
- AM6-03 records the owned-path gap correctly.

### Item 5 — B2's findings outside the work

- **The SDK's `KeyError` on an undecodable 2xx body: approved; confirmed here.**
  - `delivery.py:432-435` catches any exception and keeps only `error_code(error)`. For anything but a `ChatProviderError` that is `provider_unavailable` (`chat_provider.py:65-69`), which is retryable.
  - The retry reads first, so it meets the existing object.
  - The exact-head review need not re-derive it.
- **The fixture's `ok` against the adapter's `already` for an earlier cut-off: approved; confirmed here.**
  - `_settle` records the receipt and marks the event delivered whenever the code is `None`. `already` only reaches the `Delivery` result (`delivery.py:465`), so both outcomes are delivered with the same record.
  - The excluded row is a gap in "one port contract, two subjects", though. Record it as a follow-up: the fixture answers `already` for an earlier cut-off and the row returns to the shared contract at the next change to the fixture, before P11.
- **The nine shared packages at later versions: condition 5.1.**
  - **The issue.** The live rows will show the adapter under the harness's lock. The API's development lock resolves `pydantic` 2.14.1, `pydantic-core` 2.50.1, `pydantic-settings` 2.16.1 and **`python-dateutil` 3.0.0**, against the harness's 2.13.5, 2.46.5, 2.15.0 and 2.9.0.post0. `python-dateutil` is a major-version change.
  - **Why it matters.** The SDK decodes responses with these packages. The adapter's revocation compares a decoded `revoke_tokens_issued_before` with the cut-off (`chat_provider_stream.py`, `revoke_user_tokens`). The live evidence would then not vouch for the lock the API merges.
  - **5.1 The condition.** Before the live rows (3.3):
    - regenerate the API's development lock with the harness's `requirements.lock` as a constraint, so that every package the two share has the same version and hashes;
    - extend the pin test from three packages to every shared one;
    - leave `tzdata`, which only the API holds, as resolved.
- **The harness's `ServerApi` letting the SDK read five pool-setting names: approved as a recorded limit.** P11's runtime client passes every setting. The P11 plan records it.
- **`npm ci`'s high-severity advisory: approved.** B2-C1 names the package and advisory (its check 3). The follow-up is decided before Stage C, whose mobile app has its own lock. The harness's client is proof-only and never shipped.
- **uv 0.12.17 missing from the pinned toolchain: approved** as a follow-up for `scripts/bootstrap-toolchain.sh`.

### Item 6 — Production, and the D8 question: referred to Nathan

**The P11 drift check: approved.** Point i's generic coverage, run before each deploy and on a schedule, with an alert. The brief records it with 2.4's differential apply and item 4's creator note.

**My view: ADR 0003's trigger "a client-reachable path appears that the display rule or a design constraint does not close" is met, by three of the four additions:**

- **D1:** a client write into the match channel (scheduled messages), outside Glow's send checks;
- **D2:** a Glow-issued token able to create and join calls with the other member in a new call type;
- **D4:** client grants in a new chat type, beside the match channel and outside its removal.

The display rule does not close them: they are writes and contacts, not renderings. No design constraint closes them either. The "read-channel only" constraint is a configuration Stream changed without notice, and only detection and a re-apply restore it. The window between Stream's change and Glow's detection is open in production whatever the check's interval. Here it was up to 26 days. This is the harm Glow's block exists to prevent: contact the other person did not agree to, through a surface Glow does not see.

**So the alternative goes to Nathan before Stage C**, as DM-13 7.1 and ADR 0003's "Revisit when" require. The manager's timing is right: after B2-C1's live rows, which show what removal, deactivation and revocation actually end at Stream, and before Stage C's prompt. It does not block B2-C1, which is server-side.

**What OD-32's message should hold:**

- **What happened:** the four additions, with their dates and what each lets a client token do.
- **What breaks under each choice:**
  - **(a) Keep the client token** (`read-channel`), with P11's drift check before each deploy and on a schedule, an alert, and an application-wide token revocation on detection. The exposure is the detection window, with each new Stream surface a new instance.
  - **(b) No client token:** Glow serves history and realtime itself. Every provider-side permission path closes by construction. It needs Glow's own realtime transport, changes ADR 0003, and makes Stage C's client SDK adapter unnecessary. B2's adapter and server sends stay.
- **The manager's costing of (b)** for P11 and Stage C.
- **The recommendation.** Mine, subject to that costing, is **(b)**. DM-13 kept the token because the evidence then closed every client path. B2's baseline shows the closure depends on a provider that adds client grants without notice, and (a) can only shorten the window. If (b)'s cost is out of proportion, (a) with the safeguards above is the fallback, and that is Nathan's risk acceptance.

### Item 7 — The governing changes since DM-16: confirmed

At `5ae3c23`, against `2f62b1e`:

- **The CI policy:** after "checks no proof container remains", the clause "; the job's timeout is 30 minutes (DM-16), and its race budgets, which define the evidence, are unchanged: a run of record that takes more than 24 minutes is a finding to diagnose before acceptance (OD-21)". Word for word, as DM-16 6.1 gave it.
- **Step 7's "Wait for Codex":** ends with DM-16's *consider* clause, word for word.
- **Step 3:**
  - It carries 7.1's words. They are joined to their sentence as "this sentence names v8.2 at Nathan's direction (22 October 2026, OD-42)", a grammatical join with no change of meaning.
  - It carries 7.2's second option: the installed skill as the authority, the HD engine record as history.
  - OD-42 is in the register, and OD-34's state is marked.

**Not covered:** `9371e24` and `d9f6c1e`, which add OD-43 to step 3, the register and the environment inventory. They are governing Markdown and come to me before B2's PR merges. A prompt that would send a task to Nathan's CLI agent in an open environment comes to me before it runs, if it carries a credential.

### Item 8 — Notion

- ***Implementation Control*:**
  - It is matched to `d9f6c1e`, the live head, and its status names OD-43 and B2's pick as the repository does.
  - Its procedure's model bullet names request v8.2, OD-42 and four models (DM-16 item 8, corrected).
- **The Work Register's P06.2 row** is "Blocked", matching `5ae3c23`: B2's stop, brief revision 5, B2-C1 revision 1 and DM-17.
- ***Dev Manager — reviews and approvals*:**
  - DM-16's disposition and DM-17's pending row match the review log.
  - DM-15's verdict is now complete.
- **The uses table:**
  - B2's revision 2 row and B2-C1's revision 1 row match their prompt headers: scores 3.98 and 3.97, every rung and model probability, the 24 cells and the send times.
  - **Two mismatches:**
    - B2's revision 2 pick is "pending", while `d9f6c1e` records Nathan's pick as Fable 5.1 with no rung. The table has no option for a model without a rung (as "Opus 5.5 (level as recorded)" exists), so one is needed.
    - B2's revision 1 row is still "pending", though revision 1 never ran. Earlier rows mark such a revision not run and superseded (C2's revision 1).

## 4. Verdicts

| Item | Verdict |
|---|---|
| 1 | Approved; D3 with condition 1.1 (the baseline keeps the pre-lockdown client grants) |
| 2 | Approved with 2.1 to 2.4; iv: the general apply, with the full comparison |
| 3 | Approved with 3.1 to 3.4; revision 1 does not run |
| 4 | Approved, all three |
| 5 | Approved, with 5.1 (lock alignment before the live rows) |
| 6 | Drift check approved; D8 trigger met; referred to Nathan after B2-C1's live rows, before Stage C |
| 7 | Confirmed; `9371e24` and `d9f6c1e` not covered |
| 8 | Matches, apart from two uses-table rows |

## 5. Questions for Nathan

One, carried by the manager in OD-32's form after B2-C1's live rows and before Stage C's prompt, as item 6 describes: keep the client chat token with a drift check (a), or move to no client token (b). My recommendation, subject to the manager's costing, is (b).

## 6. Documentation to update

- **The B2-C1 prompt, revision 2:** 1.1, 2.1 to 2.4, 3.1 to 3.4, 5.1; then score it again.
- **Brief revision 5:**
  - D3's row and point ii (1.1);
  - points i and iii (2.1, 2.3);
  - point iv's production note (2.4);
  - point v (item 4's P11 note);
  - point vi (item 6).
- **The architecture document's section 5:** the "Restoring" sentence names the new baseline (with B2-C1's record).
- **The P11 plan:**
  - the drift check;
  - a differential chat apply under a guard;
  - a server-only creator;
  - the runtime client passing every pool setting.
- **Follow-ups:**
  - the fixture's earlier-cut-off answer and its contract row;
  - the npm advisory, before Stage C;
  - uv in the toolchain.
- **Notion:** the two uses-table rows.
- **The review log:** DM-17's disposition. The next consultation covers `9371e24` and `d9f6c1e`.

## 7. Limits

- **Stream's behaviour.** I did not read Stream's documentation in this read. Two things are inferred from the grant names in B2's record and from the harness's code, not observed:
  - what `schedule-message` and the `agent` types allow a client to do;
  - whether a scheduled message fires after a removal.
- **The code.** I read the adapter's operations and the parts of the harness named in section 1. I did not read `conformance.py`, the tests or the fakes.
- **The live head's last two commits** are not covered (item 7).
- **Nothing was run**, and no live call was made.
- **Notion:** the four pages in section 1 only.
- **No scoring** (OD-15).

## 8. Relay message for Nathan to paste into App Manager 6's session

> **From Dev Manager 2 to App Manager 6 (relayed by Nathan, 23 October 2026)**
>
> DM-17 is answered on `claude/dev-manager`, in `docs/continuity/dev-manager/reviews/2026-10-23-dm-17-p06-2-stage-b2-drift-read.md`. My read covers `5ae3c23`, with the code at `957dccb`. `9371e24` and `d9f6c1e` (OD-43) are not covered and come to me before B2's PR merges.
>
> **B2-C1's revision 1 does not run as it is:** its baseline check would stop it. A revision 2 that applies my conditions as written needs no further read. Score it again.
>
> 1. **D1 to D4: approved.** D3 has one condition: the 27 September products baseline holds the client roles' *pre-lockdown* grants (for example `audio_room` `user` 29), and today's snapshot holds them empty. The new baseline must take those client grants from the 27 September file for every scope it holds, and everything else from the fresh snapshot. Otherwise item 4.2's "agent and lifecycle only" check fails on every known scope.
> 2. **Points i to iv: approved with conditions.**
>    - List the application settings' unnamed keys too, with the same stop.
>    - Owned paths for the baseline merge.
>    - **Before and after each apply, compare full snapshots** (application settings and grants, every channel type, call type and feed visibility, named volatile fields aside): only D1 and D4, then D2, may change.
>    - iv: **the general `configure --apply`**, which runs outside the guard as on 25 September, with that comparison. A differential chat apply under a guard goes to P11.
> 3. **Authority and safety: approved with conditions.**
>    - Item 4.2 as above; 4.3 and 4.4 with the comparison, 4.3 saying the apply is outside the guard.
>    - The lock alignment (5) as an offline item before the live run, with its three owned paths.
>    - A part-applied state reported with its requests and comparison, not repaired.
> 4. **B2's three changes: approved.** For P11: a server-only creator identity, so no member owns the channel if Stream adds an owner-scoped grant.
> 5. **Findings: approved.**
>    - Delivery keeps the `KeyError` as retryable, and treats the fixture's `ok` and the adapter's `already` alike: both confirmed from `delivery.py`. The excluded contract row returns when the fixture next changes, before P11.
>    - **Condition:** before the live rows, regenerate the API's development lock with the harness's lock as a constraint, and extend the pin test to every shared package. `python-dateutil` 3.0.0 against 2.9.0 is a major version, and the SDK decodes the cut-off the adapter compares.
> 6. **Drift check approved. The D8 trigger is met,** by D1 (scheduled messages into the match channel), D2 (calls with the other member) and D4 (a new chat type with client grants). No design constraint closes them; only detection does.
>    - **Referred to Nathan** in OD-32's form after B2-C1's live rows and before Stage C's prompt: (a) keep the token with the drift check, or (b) no client token.
>    - My recommendation, subject to your costing of (b): (b). It does not block B2-C1.
> 7. **Governing changes: confirmed,** DM-16's words as written.
> 8. **Notion matches,** apart from two uses-table rows:
>    - B2 revision 2's pick still "pending", though the repository records Fable 5.1 with no rung; the table needs an option for that;
>    - B2 revision 1 not marked "not run".

Status: complete
