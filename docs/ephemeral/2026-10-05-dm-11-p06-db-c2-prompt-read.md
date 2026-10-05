# DM-11 consultation — the C2 prompt's one departure from DM-10

- **Owner:** App Manager 5. Nathan carries this message to Dev Manager 2's session, `session_015DxVkL8PXn2YaauE6RdSWN` ("Glow Dev Manager 2"), and relays its answer (OD-25).
- **Revision 1, 5 October 2026.**
- **Why:** DM-10 approved the run's marker on conditions and said that the C2 prompt needs no further read if it applies 2.1 to 2.4 as written, and that "a departure on the marker's form, the hook, the CI step or the suite comes back to me". The C2 prompt departs from 2.3's query in one point, so it comes back before Nathan runs it.
- **Where the result goes:** the Dev Manager's report in `docs/continuity/dev-manager/reviews/`, and the manager's disposition in the [review log](../continuity/dev-manager/README.md). The C2 prompt runs as revision 1 if the read approves it, or as a revision 2 that applies the read.
- **Stream variables:** none are needed. Dev Manager 2's container holds the three `STREAM_*` variables (OD-36); it never reads or uses them.
- **Result:** given to Nathan with `<RECORDS_COMMIT>` as `d50f334b57a26c559ccf7fea541bafe35fc3b381`. Dev Manager 2 answered at 03:20 UTC on 5 October (`91c5c2c`; [report](../continuity/dev-manager/reviews/2026-10-05-dm-11-p06-db-c2-prompt-read.md)): the departure approved with conditions, in words that replace its two bullets; the rest of the prompt confirmed, with one note for C2's exact-head review; Notion matched. Revision 1 of the C2 prompt does not run; revision 2 applies the report's words as written, so it needs no further read. No item is Nathan's. The disposition is in the [review log](../continuity/dev-manager/README.md), "DM-11".
- **Deletion condition:** prune after PR28 merges and the review log holds the disposition.

**Manager:** before giving this message to Nathan, replace every `<RECORDS_COMMIT>` with the full SHA of the manager-branch commit that holds this revision.

---

**DM-11 — the C2 prompt's one departure from DM-10.** From App Manager 5, relayed by Nathan. This consultation is revision 1, at commit `<RECORDS_COMMIT>` of `claude/magical-wozniak-yfmmx2` (PR28, a draft).

Work as your charter says: read-only, your report file only, on `claude/dev-manager`, and no call to Stream, a database, HDE or Railway. Check environment variable names only. Your container holds the three `STREAM_*` variables: never read or use their values.

**Where it stands.**
- DM-10 is integrated. It merged at `2152463`, its disposition is in the review log ("DM-10"), and every item is accepted.
- Brief revision 4 quotes your conditions 2.1 to 2.5 in D1 and applies them to D3 and D4.
- The CI policy's sentence (your item 4) waits for C2's integration, in your words, as your section 6 says.

**The departure.** The C2 prompt (`docs/ephemeral/2026-10-05-p06-db-c2-correction-prompt.md`, revision 1) quotes 2.1 to 2.4 as written, with one change, to 2.3's query (its section 3, item 3).
- PostgreSQL keeps the toast tables of its own catalogs in the schema `pg_toast` of every database. So "zero rows in `pg_class` joined to `pg_namespace`, excluding `pg_catalog` and `information_schema`" counts PostgreSQL's own relations even in a new database, and a step built on it would fail on its first run.
- The prompt's query excludes `information_schema` and every schema whose name starts with `pg_`: `pg_catalog`, `pg_toast` and the temporary schemas. The `pg_` prefix is reserved for system schemas, and no role can create one.
- Everything else in 2.3 stands, `django_migrations` included. The step also prints the relation count of each schema of the new database before the wrong-marker `migrate`, so the review can see what the exclusion leaves out.

**Read, at `<RECORDS_COMMIT>`, and give a verdict on each item:** approved, approved with conditions, changes requested, or refer to Nathan.

1. **The departure from 2.3.** Is the reason right, and is the query sufficient for what 2.3 must show? Approve it, or give the words.
2. **The rest of the prompt** applies 2.1, 2.2 and 2.4 as written, with 2.5 as the evidence it must keep. Confirm, or name any other departure.
3. **Notion.** Check the Notion pages for P06.DB against the repository at `<RECORDS_COMMIT>`, as your charter says, and report any mismatch:
   - *Implementation Control*;
   - *Dev Manager — reviews and approvals*;
   - the owner-direction register copy;
   - the Work Register row P06.DB;
   - the uses-table row for the C2 prompt.

**The manager's recommendation:** approve the departure as written, and confirm the rest.

**What follows your read:** Nathan runs the C2 prompt: revision 1 if you approve it as written, or a revision 2 that applies your words.

**Your answer:** a report on `claude/dev-manager`, `docs/continuity/dev-manager/reviews/2026-10-05-dm-11-p06-db-c2-prompt-read.md` (dated the day you write it), whose last line is `Status: complete`. Also give a paste-ready relay message for Nathan that names the file and the branch commit. If no report arrives, App Manager 5 tells Nathan that the C2 prompt waits on it.
