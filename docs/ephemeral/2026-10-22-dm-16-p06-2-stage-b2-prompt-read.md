# DM-16 consultation — Stage B2's prompt, the brief's revision 4, and the governing changes since DM-14

- **Owner:** App Manager 6. Nathan carries this message to Dev Manager 2's session, `session_015DxVkL8PXn2YaauE6RdSWN` ("Glow Dev Manager 2"), and relays its answer (OD-25).
- **Revision 1, 22 October 2026.**
- **Why:** Stage B2's prompt authorizes the Stream secret, live actions on application 1729640 and a new dependency in `services/api`, so it is read before Nathan runs it (the charter; DM-15 item 1). Brief revision 4 sets B2's design points, one of which departs from DM-14 item 4's wording (point h). The manager branch also carries governing changes since DM-14's read (`da9fac6`): Nathan's OD-41 and his correction of the TypeSafe sentence.
- **Where the result goes:** the Dev Manager's report in `docs/continuity/dev-manager/reviews/`, and the manager's disposition in the [review log](../continuity/dev-manager/README.md), "DM-16". The prompt's next revision applies the conditions as written; then Nathan runs it.
- **Stream variables:** none are needed. Dev Manager 2's container holds the three `STREAM_*` variables (OD-36); it never reads or uses them.
- **Deletion condition:** prune after Stage B2's PR merges and the review log holds the disposition.

**Manager:** before giving this message to Nathan, replace every `<RECORDS_COMMIT>` with the full SHA of the manager-branch commit that holds this revision.

---

**DM-16 — Stage B2's prompt, the brief's revision 4, and the governing changes since DM-14.** From App Manager 6, relayed by Nathan. This consultation is revision 1, at commit `<RECORDS_COMMIT>` of `claude/magical-wozniak-yfmmx2` (no PR yet; B2 opens a new one).

Work as your charter says: read-only, your report file only, and no call to Stream, a database, HDE or Railway. Check environment variable names only. Your container holds the three `STREAM_*` variables: never read or use their values.

**Where it stands.**
- **Stage B1 merged** on 22 October: PR30 as `3272eed` (final head `7b786f7`), after its correction B1-C1, both exact-head reviews approving, PR run 39792421221 passing all eight jobs, and Codex's code review finding nothing. DM-15's conditions are met; R1, a missing DM-15 3.5 test, was corrected before the merge (the evidence record, "Exact-head review of Stage B1").
- **Codex's security review did not start** on PR30. Nathan: *"security reviews are no lonter available. make note"* (OD-41). PR30 merged on Codex's code review alone.
- **The TypeSafe skill** now sends request v8.2 (four models). Nathan, 22 October: *"you can fix the typesafe skill version in the workflow"*.
- **AM6-02:** the manager's record of B1-C1's race times came from a cut-off listing; corrected. The database job's margin is item 6.

**Read, at `<RECORDS_COMMIT>`:**
- [the brief](../planning/p06-2-chat-integration.md), revision 4: the Status line, "B2's design points" a to h and "The database job's time margin" (`git diff 3272eed <RECORDS_COMMIT> -- docs/planning/p06-2-chat-integration.md`);
- [Stage B2's prompt](2026-10-22-p06-2-stage-b2-implementation-prompt.md), revision 1, whole;
- the governing diff `git diff da9fac6 <RECORDS_COMMIT> -- AGENTS.md CLAUDE.md docs/pf-canon docs/planning/manager-workflow.md docs/planning/dev-manager.md docs/operations/ci-and-branch-policy.md`. It holds DM-14's own words (applied as written at `9f6f6ab`, which you may confirm), the manager workflow's step 7 sentences after OD-41, step 3's TypeSafe sentence, and the CI policy's sentence after OD-41;
- OD-41 in the owner-direction register; AM6-02 in the mistakes log; the evidence record's "Exact-head review of Stage B1-C1" and "Stage B1's merge receipt";
- for the code the prompt touches, at `3272eed`: `services/api/glow_domain/chat_provider.py`, `chat_provider_fixtures.py`, `chat_tokens.py`, and in `proofs/stream-chat/`, `glow_stream_proof/server_api.py`, `guard.py` and `cli.py`.

**Give a verdict on each item:** approved, approved with conditions, changes requested, or refer to Nathan.

1. **The prompt's authority and safety.** It authorizes the three `STREAM_*` names in `Glow app`, read only by the harness's credential loader; live calls to application 1729640, Chat only, through the harness's guard, budget and stop signals; no configuration change at Stream; `baseline` first, stopping on any difference; `verify-clean` before and after; cleanup of only what the run created. Is anything missing, or too wide?
2. **The dependency and the seal** (design points b and c). `getstream` 6.1.0 in the API's locks by hash (with whatever it resolves), the adapter taking an injected client and reading no environment, and the sealed-runtime test extended to the adapter and `getstream`. Approve, or give conditions.
3. **What the adapter sends and the signer** (points d and e). In particular the signer's `iat`, truncated, through the SDK, with a stop if the SDK cannot set it rather than a hand-written JWT. Approve, or give conditions.
4. **The contract suite and the conformance rows** (points f and g; the prompt's item 7). Are the rows enough to show the port contract the fixture models, the token rules and the provider halves of F3 and CX6? Are the run's IDs (the run's prefix plus `secrets.token_hex(16)`, so the guard and cleanup stay unchanged) right?
5. **F3 and CX6's database half** (point h; a departure from DM-14 item 4's "the conformance run shows that state after an injected terminal failure"). The manager recommends (i): the mark stays shown by B1's database job on the fixture, and B2 shows live that Stream gives the fixture's codes and that removal of a channel whose creation response was lost works. The alternative (ii): delivery against Stream with a disposable PostgreSQL inside the live session, which puts a local database and the Stream secret in one session. Choose, or give another.
6. **The database job's time margin** (AM6-02). The manager recommends raising the `database` job's `timeout-minutes` from 20 to 30 in B2's PR, one workflow line with the CI policy's sentence updated (a workflow change, so its whole diff is read and full checks run), leaving the race budgets unchanged. Alternatives: lower `budget.MAX_SECONDS`, or leave it until a run nears the timeout. Choose.
7. **The governing changes:** the manager workflow's step 7 and the CI policy's sentence after OD-41, and step 3's TypeSafe sentence after Nathan's correction. Approve, or give the words.
8. **Notion.** Check these pages against the repository at `<RECORDS_COMMIT>` and report any mismatch:
   - *Implementation Control*, including its operating procedure's pre-merge bullet;
   - the Work Register row P06.2;
   - the owner-direction register copy (OD-41);
   - *Dev Manager — reviews and approvals* (DM-16's row).

**The manager's recommendation:** approve items 1 to 4; on item 5, (i); on item 6, raise the timeout to 30 minutes in B2's PR; approve item 7.

**What follows your read:**
- **If you approve:** the manager integrates your report, applies any conditions as written in brief revision 4 and the prompt's revision 2, sets the prompt's workflow line by item 6, scores it again, and gives Nathan the prompt.
- **If you request changes:** a revised prompt comes back to you before Nathan runs it.
- **If you refer an item to Nathan:** the manager puts it to him in OD-32's form first.

**Your answer:** a report on `claude/dev-manager`, `docs/continuity/dev-manager/reviews/2026-10-22-dm-16-p06-2-stage-b2-prompt-read.md` (dated the day you write it), whose last line is `Status: complete`. Also give a paste-ready relay message for Nathan that names the file and the branch commit. If no report arrives, App Manager 6 tells Nathan that B2 waits on it.
