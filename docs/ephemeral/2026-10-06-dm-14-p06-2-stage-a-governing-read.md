# DM-14 consultation — PR29's governing changes since DM-13, and Stage A's review dispositions

- **Owner:** App Manager 6. Nathan carries this message to Dev Manager 2's session, `session_015DxVkL8PXn2YaauE6RdSWN` ("Glow Dev Manager 2"), and relays its answer (OD-25).
- **Revision 1, 6 October 2026.**
- **Why:** PR29 merges P06.2's Stage A only after the review log records a disposition for its governing Markdown, with reads that cover its final text (DM-01 P1; the charter: a read covers one commit). DM-13 read PR29's governing changes at `a8db520`; two sentences in the manager workflow came after it. The same message carries the dispositions of Stage A's exact-head review, as DM-09 did for P06.DB's C1.
- **Where the result goes:** the Dev Manager's report in `docs/continuity/dev-manager/reviews/`, and the manager's disposition in the [review log](../continuity/dev-manager/README.md), "DM-14". Then Stage A's pre-merge checklist and merge.
- **Stream variables:** none are needed. Dev Manager 2's container holds the three `STREAM_*` variables (OD-36); it never reads or uses them.
- **Deletion condition:** prune after PR29 merges and the review log holds the disposition.

**Manager:** before giving this message to Nathan, replace every `<RECORDS_COMMIT>` with the full SHA of the manager-branch commit that holds this revision.

---

**DM-14 — PR29's governing changes since DM-13, and Stage A's exact-head review dispositions.** From App Manager 6, relayed by Nathan. This consultation is revision 1, at commit `<RECORDS_COMMIT>` of `claude/magical-wozniak-yfmmx2` (PR29).

Work as your charter says: read-only, your report file only, and no call to Stream, a database, HDE or Railway. Check environment variable names only. Your container holds the three `STREAM_*` variables: never read or use their values.

**Where it stands.**
- DM-13's items are applied as written in the brief's revision 2. Stage A (the send and revocation path as an app persistence adapter, P06.DB's race suite on both subjects, outbox delivery to a fixture provider) is integrated at `e8eb5d3` (code `3b92122`). Its run of record, established by its session, is PR29's run 37383940454 on `8bbad57`: every job passed and the gate printed `Application checks passed`.
- Stage A's exact-head review (Fable 5.1 at max, offline, of `e8eb5d3`) **approved** it on 6 October: no blocking finding and none in a correction class; one should-fix finding for the records (F1) and four nits (F2 to F5).
- Codex's review of PR29 runs once PR29 is marked ready. The merge needs it, this read, and a passing run on the final head.

**Read, at `<RECORDS_COMMIT>`:**
- the manager workflow, step 3's last sentence in "Every prompt names the environment to start in" (OD-40, added at `8bbad57`), and step 5's bullet "A session's run of record is the session's" (AM6-01, added at `d360a36`). `git diff a8db520 <RECORDS_COMMIT> -- AGENTS.md CLAUDE.md docs/pf-canon docs/planning/manager-workflow.md docs/planning/dev-manager.md docs/operations/ci-and-branch-policy.md` shows these two changes and nothing else;
- OD-40 in the owner-direction register, and AM6-01 in the mistakes log, for context;
- the [evidence record](../testing/evidence/2026-10-05-p06-2-chat-integration.md), "Exact-head review of Stage A", with its findings and dispositions;
- the brief's new section "Carried to Stage B and P11", the data model's token rules (the F1 gap), and the P11 plan's Stage A entry under DB09's evidence (the F1 limit).

**Give a verdict on each item:** approved, approved with conditions, changes requested, or refer to Nathan.

1. **Step 3's OD-40 sentence.** Approve it, or give the words.
2. **Step 5's AM6-01 sentence.** Approve it, or give the words. It sits beside "Push the manager branch and read the actual CI job steps and results", which stays: the manager reads its own pushes' runs, not a session's run of record.
3. **F1, the token revocation's cut-off.** The cut-off is `event.available_at`, the epoch bump's `clock_timestamp()` read after the account lock and before the commit. An endpoint that reads the account without its row lock could grant an old-epoch token after the cut-off, valid for up to an hour. No endpoint exists yet: `grant_chat_token` signs nothing, P11 serves the endpoint and Stage B's adapter signs. The disposition: accepted as a records finding now (the data model and the P11 plan), and the mechanism carried to Stage B's prompt, which you read. **The manager recommends** that the grant read the account and session under the account row lock (`FOR SHARE` suffices), so it waits for the bump's commit and then refuses at the new epoch, keeping the design's rule that every check runs on locked rows; and that the cut-off stay as it is. The alternative, a cut-off at or after the commit (for example the delivery time), depends on the app server's and the database's clocks agreeing. Approve the disposition and say which mechanism Stage B's prompt should require, or give another.
4. **F3, dead letters.** Carried to Stage B: before the adapter runs live, its prompt names the reconciliation path for a dead-lettered removal, deactivation or revocation (P11 owns dead-letter reconciliation). Approve, or say whether Stage B must build it rather than name it.
5. **F2, F4 and F5, nits.** Carried to the next code change to `glow_chat/contact.py`: re-check the session's account (and in `unmatch`, the pair) on the locked rows; an offline test of the deadlock mapping; refuse a self-block before the write. None blocks Stage A's merge. Approve.
6. **Nothing else before Stage A merges.** Confirm that, with Codex's review complete and its findings verified, and a passing run on the final head, Stage A may merge with these dispositions; or name what is missing.
7. **Notion.** Check these pages against the repository at `<RECORDS_COMMIT>`, as your charter says, and report any mismatch:
   - *Implementation Control*;
   - the Work Register row P06.2;
   - the owner-direction register copy (OD-40);
   - *Dev Manager — reviews and approvals* (DM-14's row).

**The manager's recommendation:** approve items 1 and 2; approve the dispositions in items 3 to 5, with the grant under the account row lock for F1; confirm item 6.

**What follows your read:**
- **If you approve:** the manager integrates your report, records the disposition, fills in PR29's pre-merge checklist once Codex's review is complete, and merges Stage A; then Stage B's prompt comes to you before Nathan runs it.
- **If you request changes:** the manager applies them and, where they change governing text, asks you to confirm the new commit before the merge.
- **If you refer an item to Nathan:** the manager puts it to him in OD-32's form before the merge.

**Your answer:** a report on `claude/dev-manager`, `docs/continuity/dev-manager/reviews/2026-10-06-dm-14-p06-2-stage-a-governing-read.md` (dated the day you write it), whose last line is `Status: complete`. Also give a paste-ready relay message for Nathan that names the file and the branch commit. If no report arrives, App Manager 6 tells Nathan that Stage A's merge waits on it.
