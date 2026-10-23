# DM-17 consultation — Stream's additions, the correction pass B2-C1, and B2's open dispositions

- **Owner:** App Manager 6. Nathan carries this message to Dev Manager 2's session, `session_015DxVkL8PXn2YaauE6RdSWN` ("Glow Dev Manager 2"), and relays its answer (OD-25).
- **Revision 1, 23 October 2026.**
- **Why:** Stage B2's live run stopped at its first command on differences that are Stream's additions, and P06.2 stopped with it (the brief's design point a; ADR 0003's condition (c)). Their disposition is a security-boundary decision. The correction pass that follows, B2-C1, authorizes the Stream secret and live configuration changes at application 1729640, so it is read before Nathan runs it (the charter). B2 also made three changes outside its prompt's words, and the CI policy took DM-16 6.1's sentence at B2's integration.
- **Where the result goes:** the Dev Manager's report in `docs/continuity/dev-manager/reviews/`, and the manager's disposition in the [review log](../continuity/dev-manager/README.md), "DM-17". B2-C1's next revision applies the conditions as written; then Nathan runs it.
- **Stream variables:** none are needed. Dev Manager 2's container holds the three `STREAM_*` variables (OD-36); it never reads or uses them.
- **Deletion condition:** prune after Stage B2's PR merges and the review log holds the disposition.

**Manager:** before giving this message to Nathan, replace every `<RECORDS_COMMIT>` with the full SHA of the manager-branch commit that holds this revision.

---

**DM-17 — Stream's additions, the correction pass B2-C1, and B2's open dispositions.** From App Manager 6, relayed by Nathan. This consultation is revision 1, at commit `<RECORDS_COMMIT>` of `claude/magical-wozniak-yfmmx2` (no PR yet; B2's PR follows B2-C1).

Work as your charter says: read-only, your report file only, and no call to Stream, a database, HDE or Railway. Check environment variable names only. Your container holds the three `STREAM_*` variables: never read or use their values.

**Where it stands.**
- **Stage B2 ran** in `Glow app` from its prompt's revision 2 (DM-16 applied as written). Its offline work is done: the Stream adapter, the signer (the pre-approved `pyjwt` route), the contract suite, the `conformance` command with 46 rows, the development-scope pin and the 30-minute database timeout. Code head `e97f90d`, records `6bdc9b8`, integrated at `957dccb`; run of record 39971426724, all eight jobs passed, the database job 8 min 31 s.
- **Its live run stopped at `baseline`,** as item 7.1 requires: 8 chat and 7 Video and Feeds differences, with 8 read-only API calls. Nothing at Stream was changed. The differences are Stream's additions since the lockdown of 27 September (the brief's table D1 to D4):
  - D1: `glow-match`'s `channel_member` also holds `schedule-message`;
  - D2: a new Video call type `agent` whose `user` (31) and `guest` (6) roles hold Stream's default grants;
  - D3: `agent` is not in the committed products baseline, and the four known call types carry a new `lifecycle` settings section;
  - D4: a new default chat channel type `agent` (created 20 October) with client grants (`user` 25, `guest` 21), which the chat target does not inspect because it names five default types.
- **The CI policy** took DM-16 6.1's sentence as written at B2's integration. **ADR 0003** and the architecture document record the first live comparison's result, factually.
- **AM6-03:** B2's prompt's owned paths did not name `services/api/pyproject.toml` or the API README, both of which a new, untyped SDK pin needs.

**Read, at `<RECORDS_COMMIT>`:**
- the evidence record's "Stage B2" (whole, especially "The live run", "The recorded choices" and "Deviations, findings and limits") and "Manager verification of Stage B2";
- [the brief](../planning/p06-2-chat-integration.md), revision 5: the Status line, B2-C1's owned paths, and "B2's live run stopped" (`git diff 2542a06 <RECORDS_COMMIT> -- docs/planning/p06-2-chat-integration.md`);
- [the B2-C1 prompt](2026-10-23-p06-2-stage-b2-c1-correction-prompt.md), revision 1, whole;
- the governing diff `git diff 2f62b1e <RECORDS_COMMIT> -- AGENTS.md CLAUDE.md docs/pf-canon docs/planning/manager-workflow.md docs/planning/dev-manager.md docs/operations/ci-and-branch-policy.md`: DM-16's own words (step 3 at 7.1 and 7.2, step 7's *consider*, the CI policy's 6.1), applied as written;
- ADR 0003's condition (c) and its "Revisit when", and the architecture document's section 4 table and section 5; AM6-03 in the mistakes log;
- for the code: at `957dccb`, `services/api/glow_domain/chat_provider_stream.py` and `services/api/pyproject.toml`; in `proofs/stream-chat/`, `glow_stream_proof/configuration.py`, `products.py`, `cli.py` (`configure`, `configure --products`, `record-products-baseline`) and `guard.py`'s configure scope, and the README's "What a run and `configure --apply` change" and "The Video and Feeds lockdown".

**Give a verdict on each item:** approved, approved with conditions, changes requested, or refer to Nathan.

1. **The disposition of D1 to D4** (the brief's table): remove D1's grant (the target stays `read-channel` alone); empty D2's client roles, as in the other call types; re-baseline for D3, with the new baseline's diff limited to the `agent` call type and the four `lifecycle` sections; lock D4 as the default types are locked. Approve, or give another disposition for any of them.
2. **B2-C1's design points i to iv.** i, the chat target covering every channel type other than `glow-match`, with `glow-match`'s unnamed fields listed and a content feature or client write among them stopping the session; ii, the new products baseline; iii, the live order; iv, the general `configure --apply`, made safe by a dry-run check that each planned request re-sends a held value or corrects D1 or D4, against the alternative of a differential chat apply like the products' (DM-05 finding 1). Approve, or give conditions.
3. **B2-C1's prompt, revision 1: authority and safety.** It authorizes the three `STREAM_*` names in `Glow app`, read only by the harness's loader; one `configure --apply` and one `configure --products video,feeds --apply`, each after its dry run and check; no `restore --apply` and no second apply; a stop on any difference beyond D1 to D4, on any failed or wrong re-read, and on a charge or limit signal; then B2's live rows from its item 7.2 with DM-16's rerun and blocking rules. Is anything missing, or too wide?
4. **B2's three changes outside its prompt's words,** made without stopping: the creator on channel creation (`created_by_id` = the first member, which Stream's server-side creation requires; a precision of DM-16 4.2's "members only"); `services/api/pyproject.toml`'s mypy override for `getstream`; and the API README's paragraph. The manager recommends accepting all three, with the exact-head review confirming that `glow-match` grants no owner-scoped permission, so the creator gains nothing beyond membership.
5. **B2's findings outside the work.** Proposed dispositions:
   - the SDK's `KeyError` on an undecodable 2xx body, propagated unmapped (DM-16 4.1): the exact-head review confirms that delivery keeps it as a retryable Glow code;
   - the fixture's `ok` against the adapter's `already` for a revocation with an earlier cut-off: kept out of the shared contract; the exact-head review confirms delivery treats both as delivered; the fixture is aligned in a later stage only if it does not;
   - the API's development lock resolving nine shared packages later than the harness's lock (`pydantic`, `pydantic-core` and `pydantic-settings` among them): the exact-head review says whether this limits what the live rows show for the API's lock;
   - the harness's `ServerApi` letting the SDK read five `STREAM_*` pool-setting names if set: a recorded limit; P11's runtime client passes every setting;
   - `npm ci`'s one high-severity advisory in the harness's unchanged client lock: B2-C1 names it, and it is carried as a follow-up;
   - uv 0.12.17, which the API README's lock command names, is not in the pinned toolchain: a follow-up for `scripts/bootstrap-toolchain.sh`.
   Approve, or give conditions.
6. **Production, and Stage C** (the brief's point vi). Stream added a call type, a channel type, a settings section and a grant on an existing role in four weeks, without notice. The manager proposes that P11 carries a drift check with point i's generic coverage, before each deploy and on a schedule, with an alert. The question: does this meet ADR 0003's trigger "a client-reachable path appears that the display rule or a design constraint does not close" (the brief's D8), which sends the no-client-token alternative to Nathan before Stage C? The manager's view is that it does in substance: D1 gave the match channel's members a client permission Glow's design withholds, and only detection and a re-apply close it. If so, the manager recommends putting it to Nathan in OD-32's form after B2-C1's live rows and before Stage C's prompt. Give your view, and refer it to Nathan if it is his.
7. **The governing changes since DM-16's read** (`2f62b1e`): confirm that step 3's sentence, step 7's sentence and the CI policy's sentence are DM-16's words as written.
8. **Notion.** Check these pages against the repository at `<RECORDS_COMMIT>` and report any mismatch:
   - *Implementation Control*;
   - the Work Register row P06.2;
   - *Dev Manager — reviews and approvals* (DM-17's row);
   - the TypeSafe uses table's rows for B2's revision 2 and B2-C1's revision 1.

**The manager's recommendation:** approve items 1 to 5; on item 2's point iv, the general `configure --apply` with the dry-run check; on item 6, the P11 drift check, and the D8 question referred to Nathan after B2-C1's live rows; confirm item 7.

**What follows your read:**
- **If you approve:** the manager integrates your report, applies any conditions as written in the brief and B2-C1's revision 2, scores it again, and gives Nathan the prompt.
- **If you request changes:** a revised prompt comes back to you before Nathan runs it.
- **If you refer an item to Nathan:** the manager puts it to him in OD-32's form first; an item that does not block B2-C1 goes to him when its moment comes, as your report says.

**Your answer:** a report on `claude/dev-manager`, `docs/continuity/dev-manager/reviews/2026-10-23-dm-17-p06-2-stage-b2-drift-read.md` (dated the day you write it), whose last line is `Status: complete`. Also give a paste-ready relay message for Nathan that names the file and the branch commit. If no report arrives, App Manager 6 tells Nathan that P06.2 waits on it.
