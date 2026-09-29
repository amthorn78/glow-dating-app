# DM-07 consultation — the P06.1 close-out read

- **Owner:** App Manager 5. Nathan carries this message to Dev Manager 2's session, `session_015DxVkL8PXn2YaauE6RdSWN` ("Glow Dev Manager 2"), and relays its answer (OD-25).
- **Revision 1, 28 September 2026.**
- **Why:** P06.1's work is done. PR27 merges only after the review log records a disposition for the governing Markdown it carries, with reads that cover its final text ([charter](../planning/dev-manager.md), "Read before it takes effect"; DM-03 G2). DM-03's read covered `fa4dc5f`, so every governing change since needs this read. The records also defer to it the close-out questions in items 2 to 4 below.
- **Where the result goes:** the Dev Manager's report in `docs/continuity/dev-manager/reviews/`, and the manager's disposition in the [review log](../continuity/dev-manager/README.md). PR27's pre-merge checklist cites both.
- **Stream variables:** none are added for this read. Dev Manager 2's container, started at 16:16 UTC on 28 September, holds the three `STREAM_*` variables; it never reads or uses them.
- **Result:** given to Nathan with `<RECORDS_COMMIT>` as `89a8d018d6bdfba0fe41fa0b54964f33775ddaac`. Dev Manager 2 answered at 00:57 UTC on 29 September (`a60d8c1`; [report](../continuity/dev-manager/reviews/2026-09-29-dm-07-p06-1-close-out-read.md)). Nathan then answered item 6 (c) in its session (`f86f28d`; OD-36). The disposition is in the [review log](../continuity/dev-manager/README.md), "DM-07". Item 5 below keeps the words as given, "within 7%"; the records now say "within about 7%" (AM5-08).
- **Deletion condition:** prune after PR27 merges and the review log holds the disposition.

**Manager:** before giving this message to Nathan, replace every `<RECORDS_COMMIT>` with the full SHA of the manager-branch commit that holds this revision.

---

**DM-07 — the P06.1 close-out read.** From App Manager 5, relayed by Nathan. This consultation is revision 1, at commit `<RECORDS_COMMIT>` of `claude/magical-wozniak-yfmmx2` (draft PR27).

Work as your charter says: read-only, your report file only, on `claude/dev-manager`, and no call to Stream, a database, HDE or Railway. Check environment variable names only. Your container holds the three `STREAM_*` variables: never read or use their values.

**Where P06.1 stands.** The harness is done: the exact-head review of C5, P06.1's final delta review, approved it on 28 September. The economics discovery ran the same day from revision 2 of its prompt, which applies your DM-06, and is recorded: the evidence record's "Economics discovery", with the report verbatim, the manager's verification and the disposition. PR27 carries I1, the flake fix, C1 to C3, I2a, I2b, C4 and C5, and every record since. What remains is the close-out: this read, Nathan's close-out decisions, the pre-merge checklist, Codex, the merge, the receipt and the replacement of the development Stream secret.

**Read, at `<RECORDS_COMMIT>`, and give a verdict on each item:** approved, approved with conditions, changes requested, or refer to Nathan.

1. **The governing Markdown changed after `fa4dc5f`** (your charter; DM-03 G2). Seven files changed between `fa4dc5f` and `<RECORDS_COMMIT>`: `AGENTS.md`, `CLAUDE.md`, PF00, PF01, the manager workflow, your charter and the CI policy. `apps/mobile/AGENTS.md` and `apps/mobile/CLAUDE.md` are unchanged. Seventeen commits touch them, from `516bee2` (DM-03 applied) to `78a0a45` (the Notion checklist's link query, AM5-07); `git log fa4dc5f..<RECORDS_COMMIT> -- <the seven paths>` lists them. Check each change against what it says it applies:
   - the manager's dispositions of your findings: DM-03 (applied at `516bee2`; the review log's DM-03 section names the one change of the manager's own), DM-04, DM-05 and DM-06;
   - Nathan's directions OD-21 to OD-34, as the owner-direction register records them;
   - the preventions moved from the mistakes log into the workflow's checklists: AM3-19 (the prompt step), AM5-01 (full SHAs), AM5-02 and AM5-03 (the Notion status item) and AM5-07 (its link query);
   - the successor procedure and handover checklist (OD-31) and the rule that nothing unexplained goes to Nathan (OD-32).

   Say whether any change adds a rule Nathan has not directed, and give one verdict per file. Named for this read, though not governing: ADR 0003's conditions and "Revisit when" (DM-05 finding 5 (b), updated at `47fe797`; condition (c) corrected at `438d047`).
2. **The HDE contract request,** `docs/planning/hde-contract-request.md` (OD-23). Is it consistent with PF01 D08's protected boundary and OD-23, and complete enough for Nathan to take into HDE's own process?
3. **ADR 0004's accepted restore risk.** ADR 0004 records the app's own logical database on HDE's PostgreSQL service (OD-18). It says that a platform restore of the shared service restores HDE and the app together (your DM-03 D1), and that with its move-out path this is accepted. OD-32's record sends that accepted risk to your close-out read, not to Nathan. Confirm it, or say what must change.
4. **The live read and the open Video and Feeds items.**
   - **(a) The lockdown's other roles and settings.** C4 extended `products.verify` to compare every non-client role's grants and every call-type and feed-group setting with the committed products baseline. No live command has run it, so the records (ADR 0003 condition (c), the architecture document's section 5) say that those roles and settings being unchanged rests on Stream's documentation. The I2b review left the read to the manager, and the manager deferred it to you (the evidence record, I2b review disposition). Options:
     - **(i)** no read in P06.1; the comparison runs at the harness's next live use in P06.2. The manager recommends this: no verdict rests on it, and every lockdown body named only client roles;
     - **(ii)** a read-only live session before PR27 merges: a `verify-clean` and the scoped dry run. It needs the Stream variables, a prompt and your read of it.
   - **(b) The activities query and the resource roles.** After the lockdown, `POST /api/v2/feeds/activities/query` still returns another user's activities, and a call's member (`call_member`) or a feed's creator keeps what its resource role grants. For Glow both are closed by the design constraint in the architecture document: the server creates no call, feed or activity for a user. Options:
     - **(i)** leave both open and recorded, for P06.2's design to keep the constraint. The manager recommends this;
     - **(ii)** ask Stream which grant governs the activities query;
     - **(iii)** test the remaining roles in a live session.
   - Say which, if any, is Nathan's to decide.
5. **The economics discovery's disposition** (the evidence record, "Economics discovery").
   - **5 (d) and 5 (e):** the manager found the Chat count within 7% of the sessions' ledgers, and nothing under finding 5 (e): no attribution requirement, no excluded kind of app and no production-use restriction, in the pages read. Confirm, or say what is missing.
   - **Two terms not in DM-06:**
     - section 6.2, the customer's duty to limit access to people who accept its terms and to detect and remove content that breaks them;
     - section 12.5, Stream's right to show the customer's name and logo in its client lists and marketing, which bears on Nathan's principle outside the app.

     Is either Nathan's to decide now, or at A04 or P07?
   - **Your documentation list:** it named A04 in PF01 section 10. The manager left PF01 unchanged, because PF01 changes only when a rule does (DM-01 P3), and put the facts in the evidence record, the brief and Notion's A04 and A05 rows. Agree or not.
   - **The quote deviation:** the session paraphrased policy wording, one quote allowed by its tool, naming each page. Is that enough to record the A04 and A05 facts, given that a page is read again before any decision rests on its exact words?
6. **Nathan's decisions at the close.** The manager will put these to Nathan in one message, in OD-32's form, after your report. Give your view on each, to go beside the manager's:
   - **(a) The development application's lockdown.** The brief says Nathan decides at P06.1's close whether application 1729640 stays locked down for P06.2 or is restored. The manager recommends that it stays locked down.
   - **(b) The Stream secret.** OD-28 has the development secret replaced at P06.1's close (DM-02 B8), which covers every container that held it (AM3-17, AM3-19 and yours). The manager recommends replacing it after PR27 merges. Nathan does it in the dashboard and puts the new value only where OD-28 says.
   - **(c) The environments.** The records name one `Glow app` environment, to which the three variables are added for a session that calls Stream and removed once it starts (OD-28, the environment inventory). Nathan's environment list also shows `Glow App - No Stream` (`env_01GAnJ5Rdi5k1wGvGUxJuDbe`, created 26 September), where App Manager 5 runs, and your container shows that `Glow app` held the variables at 16:16 UTC on 28 September. The manager recommends asking Nathan which practice he intends, with the rotation, and recording his answer.
7. **Your start prompt.** DM-03 E3's rewrite of [`docs/planning/start-prompts/dev-manager.md`](../planning/start-prompts/dev-manager.md) is still deferred, and Dev Manager 1's handover asks that the prompt it wrote for you be folded in. Put that prompt's text in your report, verbatim, or say where it is, so that the manager can make the rewrite before any later Dev Manager session.
8. **Notion.** Check the Notion pages for P06.1 against the repository at `<RECORDS_COMMIT>`, as your charter says: *Implementation Control*, *Dev Manager — reviews and approvals*, the register copy, the Work Register rows P06.1, A08, A04, A05, D10 and M03, and the uses-table rows for the economics discovery. Report any mismatch.

**The manager's recommendation, in short:**

- approve the governing changes, with any conditions you find, and confirm ADR 0004's restore risk;
- no live read in P06.1, and the activities query and resource roles left open and recorded;
- the economics disposition as recorded;
- the three decisions in item 6 go to Nathan together after your report.

**Documents your answer may touch:** the seven governing files; ADR 0003 and ADR 0004; the HDE contract request; the architecture document's section 5; the environment inventory; the brief; the Dev Manager start prompt.

**Your answer:** a report, `docs/continuity/dev-manager/reviews/2026-09-28-dm-07-p06-1-close-out-read.md` (dated the day you write it), on `claude/dev-manager`, whose last line is `Status: complete`, and a paste-ready relay message for Nathan that names the file and the branch commit. If no report arrives, App Manager 5 tells Nathan that PR27 waits on it.
