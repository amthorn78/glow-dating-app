# DM-20 — B2's live rows, D10's disposition, and the client-token question before it reaches Nathan

- **Consultation:** DM-20, revision 1, from App Manager 7, relayed by Nathan (OD-25).
- **Reviewer:** Dev Manager 2, `session_015DxVkL8PXn2YaauE6RdSWN`, branch `claude/dev-manager`.
- **Commit read:** `050a37e99efa411ddfdb683669a5a03331d10024`, the head of `claude/magical-wozniak-yfmmx2` (draft PR31) when I fetched it. **This read covers `050a37e`** (DM-03 G2).
- **Environment (names only):** `STREAM_APP_ID`, `STREAM_API_KEY` and `STREAM_API_SECRET` are present, never read or used. No HDE name is present.
- **What I did not do:** I called no provider, database, HDE or Railway. I ran no repository code and read no GitHub run.

## 1. What I read

**At `050a37e`:**

- **The evidence record:** "Stage B2-C3", whole, and "Manager verification of Stage B2-C3".
- **The brief's diff `7498e47..050a37e`, whole:** the Status line, D8's pointer, "B2's live rows, and what they leave" (points i to iv) and "The client-token question (D8)".
- **The D8 message for Nathan,** revision 1, whole.
- **`conformance.py`:**
  - the rows C4, M5, D10 and V13 and the identifiers they use (`_id`);
  - `_row` and `_both`;
  - `results()` and its use of `proof_run._generic` and `_TABLE_NAMES`.
- **`chat_provider_stream.py`:** `_users`, `create_channel`, `send_message`, `deactivate_user`, `revoke_user_tokens`, `_mapped` and `_send_error`.
- **`test_chat_provider_stream.py`:** `test_deactivation_and_revocation_never_create_a_user`.
- **`checks/run_plan.py`:** its docstring and `session_used`.
- **The diff `7498e47..050a37e`** over `docs/adr`, `docs/architecture` and `docs/testing/p11-deferred-acceptance.md`. I also read the architecture document's section 5 whole.
- **Other files:**
  - DM-16 items 4 and 5, for what the blocking rule protects;
  - PF01's Chat and Jobs rows, and its Redis lines;
  - the mistakes log's changes since `52552f7`;
  - `adcc0c7`, the record of the Mobile job's timeout.

**What changed since my DM-19 read (`52552f7`):**

- **Governing Markdown:** nothing. `git diff --stat 52552f7 050a37e` over the governing paths, the environment inventory included, is empty.
- **Code:** nothing under `services/`, `proofs/`, `.github/`, `apps/` or `scripts/`.

**Notion, read-only, 23 October:**

- *Implementation Control*;
- the Work Register's P06.2 row;
- *Dev Manager — reviews and approvals*;
- the uses table's B2-C3 rows.

## 2. Verdicts

| Item | Verdict |
|---|---|
| 1 D10's disposition | **(b), approved with conditions 1.1 to 1.3** |
| 2 M5 and R7 | **Approved with condition 2.1.** No adapter change |
| 3 The two findings for the exact-head review | **Approved:** "for the review, not fixed now" is right, with one note on each |
| 4 The costing, and whether (b) stands | **The costing is fair, but needs four additions (4.1 to 4.4). My recommendation of (b) stands.** The socket or (b′) is a technical choice for the brief |
| 5 The message for Nathan | **Changes requested,** in the wording of section 7, which replaces its body. Revision 1 does not go to Nathan |
| 6 Condition (c) closed | **Confirmed,** with condition 6.1 on the architecture document's section 5 |
| 7 The order from here | **Confirmed, with 7.1:** the correction pass and its re-review are named in the order |
| 8 Notion | **No mismatch** |

**What needs no further read:** a message revision 2 in section 7's words, and brief revision 8 with these conditions applied as written (G2).

**What goes to Nathan:** only the D8 question, which is his. It goes in section 7's form, after this report is integrated.

## 3. Item 1 — D10: (b), with conditions

**The record and the code agree with the manager's reading.**

- **Every row names the same identifier.** `conformance.py` gives C4, M5, D10 and V13 one identifier, `self._id("U9")`, created once.
- **What C4 showed.** C4 (`create_channel`) reads both members with `_users`, a `query_users` by ID with deactivated users included. Stream returned no entry for `U9`, so the adapter raised `member_unavailable` and sent nothing.
- **How `U9` came to exist.** M5 then sent a message as `U9`. Stream accepted it, and the cleanup later found one prefixed user the run had not recorded.
- **D10.** `deactivate_user` read `U9`, found it, and deactivated it: `ok`.
- **V13.** `revoke_user_tokens` read `U9`, now deactivated, and sent the partial update. Stream answered 404 with code 16, which `_mapped` turns into `member_unavailable`.

**Why (b) is enough:**

- In `deactivate_user` and `revoke_user_tokens`, the only Stream behaviour on the absent-user path is the read. If the read finds no user, the adapter raises before any write.
- C4 showed that read live, with an ID Stream did not hold. D8 showed the same read finding a deactivated user.
- The offline test shows the branch after the read: one `GET`, `member_unavailable`, and no user created. That is what DM-16 4.4 and 5.2 ask of these rows.
- **Why not (a):** another live session and another Dev Manager round would show the same read again.

**Conditions:**

- **1.1 The record says it plainly.**
  - **Where:** the brief's point i, the evidence record's disposition, and the exact-head review's prompt.
  - **What they say:** D10 and V13 did not exercise "a user Stream does not have" live. The evidence for their cause is C4's live read (the same `_users` read, by ID, deactivated users included) and the offline test.
  - **V13 also showed something else live:** a revocation sent for a deactivated user is refused (404, code 16, giving `member_unavailable`), so no cut-off is set.
    - That is harmless while the port has no reactivation: a deactivated user's tokens are refused (D3, D7).
    - The P11 plan records that any later reactivation path re-sends the revocation after reactivating.
- **1.2 The identifier correction, in the correction pass after the exact-head review, with a test.**
  - C4, D10 and V13 each get an identifier that no other row names, and M5 gets its own.
  - A test in the harness fails if any two of those rows share an identifier.
- **1.3 M5 becomes a recorded row in the same correction, as R7 is (DM-16 4.7).**
  - Item 2 makes M5 the provider's known behaviour. Left as it is, every future live run reports a DIFFERENCE that is already dispositioned.
  - The run records M5's identifier as a user its send may create, so the cleanup deletes that user by record, not only by the prefix search that found it this time.

## 4. Item 2 — M5 and R7: approved, no adapter change

**Why the delivery order closes M5's path, as designed:**

- C4 shows that the adapter, by its read, refuses a channel that names a user Stream does not hold. So a match channel exists only between provisioned users.
- M5's path would then need a send whose sender is not one of the channel's provisioned members. That can only come from a fault in Glow: a wrong identifier mapping, or a user removed at Stream outside the design.
- A deactivated sender is refused by Stream itself (D9). A deleted channel gives `channel_unavailable` (M4).
- A read before each send would cost a call per message to guard against Glow's own fault.
- Two other defences cover it: Glow's send checks (D5) and P11's reconciliation, which reports a provider user Glow never provisioned.

**R7** is DM-16 4.7's predicted case. Glow's checks refuse a removed member's send before delivery.

**The P11 plan's new bullet (approved), with one wording condition:**

- **2.1 Wording.** "Whose provisioning has not been received" does not say received by whom. It reads instead: "for a sender whose provisioning delivery has not succeeded (Stream has not acknowledged it)".

**A note for P11, not a condition:** R7 also means that a send delivered after the channel's removal is accepted, and lands in the kept history.

- B1's order key orders events as they were written.
- A retried send whose `available_at` moves later can still be delivered after a later removal of its channel.
- P11's worker keeps per-channel order across retries, so a committed send is delivered before a later removal of its channel, or it records the case.

## 5. Item 3 — the two findings: "for the review, not fixed now" is right

- **The partial generalization.**
  - **The cause:** `results()` passes each row's detail through `proof_run._generic`, which replaces only the keys in `_TABLE_NAMES`. `U1` to `U9`, `C1` to `C4`, `CX` and `M1` to `M5` are not among them.
  - **What is exposed:** the random part of a synthetic, deleted user's ID stays in the git-ignored results. No credential is involved, and the secret scan found none in any record.
  - **Class:** not one of the fix-here classes (a credential leak, a request outside the guard, a configuration change beyond the planned scopes).
  - **Note:** it fits the correction pass of 1.2 (the same command's results), with a test that no row's detail keeps a run identifier's random part. The review decides.
- **`checks/run_plan.py`.**
  - **It works as designed.** Its docstring says the caps are per session and the plan adds this checkout's ledger. Exiting 1 after a live run in the same checkout is the budget doing its job, and a fresh checkout, as in CI, fits.
  - **Note:** if the review changes anything, it changes only the wording of the result, never the caps or the ledger's addition. "No weakened check, guard, deny-list or budget" holds.

## 6. Item 4 — the costing, and the recommendation

**The costing is fair on its main lines:**

- what (b) removes;
- what it adds before P11 and in P11;
- (b′) as a lighter start;
- that the drift check stays under (b) as hygiene;
- the canon change to PF01's Chat row ("Reuse transport/history/native UI where safe");
- that PR31 is unaffected.

**Four things are missing.** The manager adds them to the brief's costing:

- **4.1 Stream's rate limits bound (b)'s reads.** Under (b), every history page is a server-side Stream read. (b′) polls every few seconds per open conversation. Both run under Stream's per-application rate limits on server-side calls.
  - P11 sizes them.
  - The "anything new?" poll can be answered from Glow's own committed sends, since every message passes through Glow's server, so polling need not reach Stream.
- **4.2 The session count, as the record runs.** Each P06.2 stage so far has needed at least one correction pass. "About one more implementation session" reads "about one more implementation session, with its exact-head review and any correction it needs".
- **4.3 What (b) leaves open: read enforcement.**
  - Today, after an unmatch or block, Stream's membership also stops a removed member's client from reading (R3). Under (b), Glow's history check alone decides.
  - The history endpoint's tests (the costing's item 1) cover unmatch, block and suspension.
- **4.4 The Redis it names is the app's own.** "The Redis PF01 already plans for the app's jobs" means the app's Redis in PF01's Railway topology. It does not mean the shared project's Redis, whose ownership PF01 records as unresolved ("do not flush, repurpose or retire").

**Note, not a condition:** under (b) the signer and its `pyjwt` pin (development scope) go dormant with the per-user revocation. Both can be removed later.

**My recommendation of (b) stands:**

- (a)'s exposure is structural. In 26 days Stream added four client-reachable surfaces without notice, and it re-creates its default types at the application's first write (D6, and B2-C3's two call types). Detection can shorten the exposure window but not close it.
- (b) closes the client path by construction, at a cost the costing puts at about one session and one service.
- M5 and R7 add a point: Glow's own checks are already the only gate on sends under either option. (b) makes them the only gate on reads too, which 4.3 makes explicit.

**The socket or (b′): a technical choice for the brief, as proposed.** Nathan's (b) covers either, and the security model is the same. The P11 plan states which it starts with, the delay members see under (b′), and the running cost, so Nathan sees it as information and can object.

## 7. Item 5 — the message: changes requested, in these words

**What revision 1 gets wrong against the record:**

- It names "four things" and lists three.
- It says "a second kind of chat room", but six other kinds already existed.
- It says "the removals held", but they held for the length of one test run, from 21:14 and 22:29 to 22:31 UTC.
- It says (b) closes "every way a Stream change could reach a member, permanently". (b) closes the app's way in; Stream's server-side behaviour still needs the settings check.
- It gives (a) no cost line, and (b) no "what stays open" line, which OD-32's form requires.
- It calls the process "small". The costing says "to run and pay for".

**The body after the rule reads as follows.** The header bullets stay; "Revision 1" becomes "Revision 2, applying DM-20 as written".

> **DECISION NEEDED: should the Glow app hold a Stream login token at all?**
>
> **What it is.** Today's design gives each signed-in member's app a Stream token that lasts one hour and can only read their own match conversations. Everything they see is still drawn by Glow, and every message they send goes through Glow's server first, where block and unmatch are enforced.
>
> **What happened.** Between 27 September and 23 October, Stream quietly added four things to our test account that such a token could use:
>
> - scheduling a message into the match conversation without going through Glow's checks;
> - two new kinds of voice and video call that the token could start or join;
> - another kind of chat room.
>
> We found them up to 26 days later and removed them, and they were still removed at the end of that evening's test run. But Stream can add more at any time without telling us. Each time, a token in someone's app could use the new feature until we notice.
>
> **The two options.**
>
> - **(a) Keep the token, and watch for changes.** Glow checks Stream's settings before every release and on a schedule, alerts us when something changes, and can cut off every token at once.
>   - **What it costs:** the Stream chat library in the app; at launch, the token service, the checks and alerts, and the cut-off procedure.
>   - **What stays open:** the gap between Stream adding something and us catching it. Checks shorten that gap; they cannot close it.
> - **(b) No token in the app.** The app talks only to Glow. Glow also delivers conversation history and new messages to the app itself.
>   - **What it closes:** any way for a member's app to use a Stream change, because the app never holds a Stream login. We still check Stream's settings, since Glow's server uses them, but a missed change no longer reaches members' apps.
>   - **What it costs:**
>     - about one more build session, with its review, before launch (history and live updates through Glow);
>     - at launch, one more server process for live updates, to run and pay for. As a lighter start, notifications plus the app checking for new messages every few seconds while a conversation is open.
>
>     It also makes the Stream library in the app and the token service unnecessary.
>   - **What stays open:**
>     - Glow's own checks alone decide who can see a conversation; today Stream's membership also enforces it.
>     - Whether Stream is still worth its cost when only our server uses it, and how Stream counts users for billing then, are later questions, not part of this one.
>
> **What breaks if this is not decided:** nothing already built; the server-side chat work merges either way. The next stage, the chat screens in the app, is built differently under (a) and (b), so its prompt waits for this answer.
>
> **Recommendation: (b).** The Dev Manager recommends it too. It removes this risk instead of narrowing it, for roughly one extra build session and one more service. If you choose (a), you are accepting that the gap stays open between a Stream change and our check.
>
> **Your answer:** "(a)" or "(b)", plus anything you want weighed.

**Can Nathan act on it?** Yes. Every term is explained, the choice is two letters, and nothing in it is a question that is not his.

## 8. Item 6 — condition (c): confirmed, with one condition

**Why the caveat is closed:**

- B2-C2's chat apply and B2-C3's products apply each ran with a full comparison before and after.
- Every changed field was planned, derived, or an identity field under DM-19 2.4.
- The closing `baseline` read 0 and 0, and the closing view equalled V2.
- So, for the scopes these applies wrote, that the other roles' grants and the settings stay unchanged now rests on live comparisons, not only on Stream's documentation.
- ADR 0003's wording is accurate.

**Condition:**

- **6.1 The architecture document's section 5 follows the executable form.** Condition (c) names section 5 as the plan, and three of its sentences now lag the record:
  - **Step 2** lists `commerce`, `gaming`, `livestream`, `messaging` and `team`. Since B2-C1 the chat target covers every channel type other than `glow-match` (`configuration.py`), `agent` included. Step 2 reads: "for every channel type other than `glow-match` (the five above on 27 September; `agent` since P06.2 Stage B2-C1)".
  - **"No call type or visibility was created or deleted"** needs a qualification. The applies' first writes made Stream's default types the application's own:
    - the four call types on 27 September, by their stamps;
    - `agent` and `audio_call` on 23 October, measured;
    - the chat type `agent` at B2-C2's write (D6).

    The sentence says so beside "no request created or deleted one".
  - **"The plan as applied"** adds the applies of 23 October:
    - B2-C2's chat apply, eight requests;
    - B2-C3's two `PUT`s, 201 each;
    - both with full comparisons (the evidence record's "Stage B2-C2" and "Stage B2-C3").
  - **My share:** DM-17, which approved the chat target's widening, did not ask for step 2 to follow.

**The architecture document is not governing Markdown.** Applied as written in the records batch that integrates this report, it needs no further read.

## 9. Item 7 — the order: confirmed, with one condition

**7.1 The order is named in full:**

1. DM-20 integrated, with 1.1, 2.1, 4.1 to 4.4 and 6.1 applied in the same records batch;
2. the D8 message, revision 2, to Nathan;
3. the exact-head review of B2, B2-C1, B2-C2 and B2-C3, offline, in `Glow App - No Stream`;
4. **the correction pass** (1.2, 1.3, and anything the review asks for), offline;
5. **its exact-head re-review;**
6. Codex's code review of the final head;
7. PR31's merge, with the final head's run passed.

**What waits for Nathan's answer and what does not:**

- The review does not wait for his D8 answer: PR31 is server-side and unaffected either way.
- Stage C's prompt and the P11 plan's shape wait for it.

**The Mobile timeout on `52552f7`:** the record (`adcc0c7`) is a diagnosis under OD-21. The browser download took 11 min 27 s against 25 s on the same commit, and PR31 changes nothing under `apps/`. It needs no fix in PR31. The final head still needs its own passing run before the merge.

## 10. Item 8 — Notion: no mismatch

- ***Implementation Control*:**
  - "Current status — 23 October 2026 (App Manager 7; P06.2: B2-C3 integrated; DM-20 with Nathan)", last matched to `050a37e`.
  - Its account matches the repository: B2-C3, D10's block, brief revision 8, the D8 costing, and the Mobile timeout.
- **The Work Register's P06.2 row:** "In progress". Its next actions match the brief's point iv: DM-20, D8 to Nathan, the review (or option (a)'s live pass first), Codex, the merge, then Stage C.
- ***Dev Manager — reviews and approvals*:**
  - DM-19's row carries its disposition (every item accepted as written, at `7498e47`, merge `5480b99`);
  - DM-20's row reads pending;
  - both as the review log does.
- **The uses table:** B2-C3 revision 2 reads score 3.29, Opus 5.5 at extra high, Nathan's pick not recorded. That matches the prompt's header and the brief's "Sessions".

## 11. Where each condition goes

- **The brief, revision 8:**
  - point i takes 1.1 to 1.3;
  - point ii takes 2.1 and its note;
  - the D8 costing takes 4.1 to 4.4;
  - point iv takes 7.1's order.
- **The D8 message:** revision 2 in section 7's words.
- **The architecture document's section 5:** 6.1.
- **The P11 plan:**
  - 2.1's wording;
  - 1.1's reactivation note;
  - R7's ordering note;
  - 4.1's rate limits, when its realtime choice is written.
- **The exact-head review's prompt:** 1.1's statement; the two findings with section 5's notes.
- **The correction pass after the review:** 1.2 and 1.3.

Status: complete
