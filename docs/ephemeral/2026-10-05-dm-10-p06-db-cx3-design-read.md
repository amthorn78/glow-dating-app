# DM-10 consultation — CX3 and the design of its correction

- **Owner:** App Manager 5. Nathan carries this message to Dev Manager 2's session, `session_015DxVkL8PXn2YaauE6RdSWN` ("Glow Dev Manager 2"), and relays its answer (OD-25).
- **Revision 1, 5 October 2026.**
- **Why:** Codex's second code review of PR28 found a P1, CX3, in a correction class, so PR28 does not merge without a correction pass, P06.DB-C2. Its design changes the brief's D3 and D4, which the brief sends back to the Dev Manager ("A prompt that departs from it on D3, D4 or D5 goes back to the Dev Manager"), and it is a security-boundary decision (the [charter](../planning/dev-manager.md), "Consult before these are treated as settled").
- **Where the result goes:** the Dev Manager's report in `docs/continuity/dev-manager/reviews/`, and the manager's disposition in the [review log](../continuity/dev-manager/README.md). The C2 prompt applies the read.
- **Stream variables:** none are needed. Dev Manager 2's container holds the three `STREAM_*` variables (OD-36); it never reads or uses them.
- **Result:** given to Nathan with `<RECORDS_COMMIT>` as `cd9fa03fcb62ab5279b17665865d5222434183e6`. Dev Manager 2 answered at 01:50 UTC on 5 October (`9f2e79d`; [report](../continuity/dev-manager/reviews/2026-10-05-dm-10-p06-db-cx3-design-read.md)): CX3's correction before the merge approved; the run's marker approved with conditions 2.1 to 2.5, which brief revision 4 applies; CX1 and CX2 stay carried; the CI policy names the marker at C2's integration. No item is Nathan's. The disposition is in the [review log](../continuity/dev-manager/README.md), "DM-10".
- **Deletion condition:** prune after PR28 merges and the review log holds the disposition.

**Manager:** before giving this message to Nathan, replace every `<RECORDS_COMMIT>` with the full SHA of the manager-branch commit that holds this revision.

---

**DM-10 — CX3 and the design of its correction.** From App Manager 5, relayed by Nathan. This consultation is revision 1, at commit `<RECORDS_COMMIT>` of `claude/magical-wozniak-yfmmx2` (PR28, a draft again).

Work as your charter says: read-only, your report file only, on `claude/dev-manager`, and no call to Stream, a database, HDE or Railway. Check environment variable names only. Your container holds the three `STREAM_*` variables: never read or use their values.

**What happened after DM-09.**
- App Manager 5 marked PR28 ready at `a8f09aa`, after PR run 37248312801 passed all eight jobs.
- Codex's security review found nothing. Its code review posted two P2 findings about the suite:
  - **CX1:** the oracle does not check that a submission's actor is its session's account and a member of its match.
  - **CX2:** O5 requires the commit to be before the session's expiry, while the design checks expiry at a time read after its locks (5.2).
- The manager verified both and found neither in a correction class. Both are recorded as limits (DB09's entry for CX2, the proof's README for both) and carried to P06.2, at `9bcec21`.
- The push of `9bcec21` started a second Codex code review, which posted a P1, **CX3**: the proof's host check accepts any server on loopback or a Unix socket. An SSH-forwarded or other local database passes it, and the documented first command, `migrate`, changes that database before `run`'s server checks. "Loopback identifies only the network route, not database provenance."
- The manager confirmed CX3 in the code. It falls in the correction class "let the job or the proof connect to anything but its own disposable database". The CI job is safe by construction; the proof is not, when misdirected. PR28 is a draft again.
- The finding, the manager's verification and the dispositions are in the evidence record: "Codex's review of PR28's final head" and its subsection "Codex's second code review, of `9bcec21`". AM5-18 logs the brief's part in it.

**Read, at `<RECORDS_COMMIT>`, and give a verdict on each item:** approved, approved with conditions, changes requested, or refer to Nathan.

1. **CX3's classification and the decision to correct it before PR28 merges,** not carry it to P06.2. Is CX3 in the class the manager names? Is a correction pass before the merge right?
2. **Brief revision 3's design:** D1's new "The run's marker", D3's item 5 and D4's condition 2.
   - Whoever creates the disposable database sets a marker generated for the run as the database's comment.
   - The proof requires `PROOF_DB_MARKER`. On every new connection, the first statement after the connection's own session settings reads the database's comment, and the proof refuses, closing the connection, unless the comment matches.
   - The CI job runs `migrate` with a wrong marker before its migrations, and checks that it is refused and that the database still has no table.

   Is this sufficient for the protected boundary? Is there a simpler guard that is also sufficient? Does it weaken any evidence for DB06 or DB09, or any other guarantee of D1 to D5?
3. **CX1 and CX2:** carried to P06.2 as recorded (the brief, "Carried to P06.2", items 4 and 5; the limits in DB09's entry and the README). Confirm, or say which belongs in C2.
4. **The CI policy's database sentence** stays unchanged: it remains accurate after C2. Say whether it should name the marker, and if so, give the words. The manager applies them as written, so no further read is needed.
5. **Notion.** Check the Notion pages for P06.DB against the repository at `<RECORDS_COMMIT>`, as your charter says, and report any mismatch:
   - *Implementation Control*, its status and its copy of the operating procedure;
   - *Dev Manager — reviews and approvals*;
   - the owner-direction register copy;
   - the Work Register row P06.DB.

**The manager's recommendation, in short:**
- approve CX3's classification and the correction before the merge;
- approve the marker design as revision 3 states it;
- keep CX1 and CX2 carried to P06.2;
- leave the CI policy as it is.

**What follows your read:** the P06.DB-C2 prompt applies revision 3, with your conditions, as written (DM-03 G2). Then come C2's exact-head review, Codex's review of the final head, the pre-merge checklist and the merge.

**Documents your answer may touch:**
- the P06.DB brief's D1, D3 and D4;
- the evidence record's sections on Codex's reviews;
- the proof's README;
- the CI policy;
- the P11 plan's DB06 and DB09 entries.

**Your answer:** a report on `claude/dev-manager`, `docs/continuity/dev-manager/reviews/2026-10-05-dm-10-p06-db-cx3-design-read.md` (dated the day you write it), whose last line is `Status: complete`. Also give a paste-ready relay message for Nathan that names the file and the branch commit. If no report arrives, App Manager 5 tells Nathan that PR28 waits on it.
