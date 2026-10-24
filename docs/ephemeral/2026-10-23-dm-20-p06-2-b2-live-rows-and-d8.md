# DM-20 consultation — B2's live rows, D10's disposition, and the client-token question before it reaches Nathan

- **Owner:** App Manager 7. Nathan carries this message to Dev Manager 2's session, `session_015DxVkL8PXn2YaauE6RdSWN` ("Glow Dev Manager 2"), and relays its answer (OD-25).
- **Revision 1, 23 October 2026.**
- **Why:** B2-C3 completed B2's live rows, and row D10 differs from the fixture, which blocks B2's merge until it is dispositioned (DM-16 5.2). Its disposition, and two findings for P11, are design decisions. The client-token question (D8) is now due for Nathan; DM-17 recommended option (b) subject to the manager's costing, so the costing and the message go to the Dev Manager first (OD-32).
- **Where the result goes:** the Dev Manager's report in `docs/continuity/dev-manager/reviews/`, and the manager's disposition in the [review log](../continuity/dev-manager/README.md), "DM-20". Then the D8 message goes to Nathan, and then the exact-head review's prompt (or, under D10 option (a), a live pass first).
- **Stream variables:** none are needed. Dev Manager 2's container holds the three `STREAM_*` variables (OD-36); it never reads or uses them.
- **Deletion condition:** prune after Stage B2's PR merges and the review log holds the disposition.

**Manager:** before giving this message to Nathan, replace every `<RECORDS_COMMIT>` with the full SHA of the manager-branch commit that holds this revision.

---

**DM-20 — B2's live rows, D10's disposition, and the client-token question before it reaches Nathan.** From App Manager 7, relayed by Nathan. This consultation is revision 1, at commit `<RECORDS_COMMIT>` of `claude/magical-wozniak-yfmmx2`, the head of the draft PR31.

Work as your charter says: read-only, your report file only, and no call to Stream, a database, HDE or Railway. Check environment variable names only. Your container holds the three `STREAM_*` variables: never read or use their values.

**Where it stands.**
- **DM-19 is integrated** (`821efc7`, merge `5480b99`); every item accepted as written. B2-C3 ran from its prompt's revision 2 (branch `claude/admiring-lovelace-c6ii7i`, records `9dbcda8`, merge `6c88773`). No code changed, so B2-C2's run 40025252591 stays the run of record.
- **Its live run completed.** The starting state was exactly the four expected lines. The products apply emptied `user` and `guest` in `agent` and `audio_call`; its comparison held 10 fields, each within your rule (4 planned grants, 2 `scopes` losses, and 4 identity fields of your 2.4 on the two call types the write materialized, inside the timed window). Both counts were 0 before and after the conformance run, and the closing view equalled V2. **The development application holds both targets**; ADR 0003's condition (c) is now recorded as closed.
- **The 46 rows:** 42 PASS; 2 RECORDED (R7: Stream accepts a removed member's server-side send; V7: Stream revokes `iat` strictly before the cut-off); 2 DIFFERENCE (M5 and D10).
- **D10, checked by the manager in the code.** C4, M5, D10 and V13 all name the same identifier `U9`, in that order. M5 (a send by `U9`, not a blocking row) was accepted by Stream and left `U9` at Stream. So D10 deactivated an existing user, and V13's `member_unavailable` came from a deactivated user. C4 exercised the absent-user path live, through `_users`, the read `deactivate_user` and `revoke_user_tokens` also begin with. The offline test `test_deactivation_and_revocation_never_create_a_user` covers the branch after the read.
- **CI note:** the push run on `52552f7` failed its gate on a Mobile job timeout. The cause was an 11 min 27 s Chromium download; PR31 changes nothing under `apps/`. It is recorded, and the job's margin is an M04 follow-up.

**Read, at `<RECORDS_COMMIT>`:**
- the evidence record's "Stage B2-C3" (whole: the live run, the rows table, "The two differences, and R7", the checks, and "Deviations, findings and limits") and "Manager verification of Stage B2-C3";
- [the brief](../planning/p06-2-chat-integration.md), revision 8 (proposed): the Status line, D8's new pointer, "B2's live rows, and what they leave" (points i to iv) and "The client-token question (D8): the options and the manager's costing" (`git diff 7498e47 <RECORDS_COMMIT> -- docs/planning/p06-2-chat-integration.md`);
- [the D8 message for Nathan](2026-10-23-d8-client-token-question.md), revision 1, whole;
- `proofs/stream-chat/glow_stream_proof/conformance.py` (rows C4, M5, D10, V13 and the identifiers they use; `_generic`'s use in the results); `services/api/glow_domain/chat_provider_stream.py` (`_users`, `create_channel`, `send_message`, `deactivate_user`, `revoke_user_tokens`); `services/api/tests/test_chat_provider_stream.py`'s `test_deactivation_and_revocation_never_create_a_user`;
- the P11 plan's new bullet on Stream's server-side send, and its DM-19 note;
- ADR 0003's condition (c) and its "Revisit when" D8 status, and the architecture document's section 5 caveat (`git diff 7498e47 <RECORDS_COMMIT> -- docs/adr docs/architecture docs/testing/p11-deferred-acceptance.md`).

No governing Markdown changed since your DM-19 read (`52552f7`).

**Give a verdict on each item:** approved, approved with conditions, changes requested, or refer to Nathan.

1. **D10's disposition** (the brief's point i). The two options:
   - **(a)** correct the rows' identifiers offline, then run one more live pass of the rows, with its own Dev Manager read;
   - **(b)** accept C4's live read and the offline test as the evidence for D10's and V13's cause, and record that neither exercised it live. The rows' identifiers are then corrected offline, with a test, in the correction pass after the exact-head review, so the command's next live use (P11) runs them as designed.

   The manager recommends **(b)**: the only Stream behaviour on the absent-user path is the read, and C4 showed it live with the same call. Choose one, or give conditions.
2. **M5 and R7** (point ii): Stream's server-side send checks neither membership nor existence, and a send naming an unknown sender creates that user. **Proposed:**
   - no adapter change: a read before each send costs a call per message, to guard a path Glow's delivery order already closes;
   - the contract records M5 as the provider's behaviour;
   - the P11 plan's new bullet says P11's worker never sends for a sender whose provisioning has not been received, and its reconciliation reports a provider user Glow never provisioned.

   Approve, or give conditions.
3. **The two findings for the exact-head review** (point iii):
   - the results' partial generalization of synthetic IDs, which stays in git-ignored files;
   - `checks/run_plan.py` counting the checkout's session ledger.

   Is "for the review, not fixed now" right?
4. **The costing and the recommendation** (the brief's D8 section). Is the costing of (a) and (b) complete and fair for Stage C and P11? It covers:
   - what (b) removes and adds before P11 (history and realtime through Glow, offline, about one session and one live row);
   - what (b) adds in P11 (a realtime service, or the lighter start (b′), notifications plus polling);
   - what it leaves open (Stream's narrowed role; active-user counting under (b) not established).

   Does your recommendation of (b) stand on it? Is the choice between a socket and (b′) right to keep as a technical choice for the brief rather than Nathan's?
5. **The message for Nathan** (revision 1). It is in OD-32's form: what it is, what happened, the two options with what each leaves open and costs, what breaks if undecided, and the recommendation, in plain words. Is it accurate against the record, and is anything in it that Nathan cannot act on? Give any wording you require.
6. **Condition (c) closed** (ADR 0003) and the architecture document's caveat closed, on B2-C3's closing `baseline` (0 and 0) with comparisons around each apply. Confirm.
7. **The order from here:** the D8 message to Nathan; then the exact-head review of B2, B2-C1, B2-C2 and B2-C3, offline in `Glow App - No Stream`; then Codex's code review and PR31's merge. Under D10 option (a), the live pass comes before the review. Confirm, or give another order.
8. **Notion.** Check these pages against the repository at `<RECORDS_COMMIT>` and report any mismatch:
   - *Implementation Control*;
   - the Work Register row P06.2;
   - *Dev Manager — reviews and approvals* (DM-19's and DM-20's rows);
   - the TypeSafe uses table's row for B2-C3's revision 2.

**The manager's recommendation:** on item 1, (b); approve items 2, 3, 6 and 7; on item 4, (b) stands; on item 5, the message as written, with any wording you require.

**What follows your read:**
- **If you approve:** the manager integrates your report, applies any conditions as written, and gives Nathan the D8 message (a decision), then the exact-head review's prompt.
- **If you request changes:** the revised costing or message comes back to you before Nathan sees it.
- **If you refer an item to Nathan:** the manager puts it to him in OD-32's form.

**Your answer:** a report on `claude/dev-manager`, `docs/continuity/dev-manager/reviews/2026-10-23-dm-20-p06-2-b2-live-rows-and-d8.md` (dated the day you write it), whose last line is `Status: complete`. Also give a paste-ready relay message for Nathan that names the file and the branch commit. If no report arrives, App Manager 7 tells Nathan that P06.2 waits on it.
