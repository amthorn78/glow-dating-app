# DM-12 consultation — `dbshell` and DM-10's condition 2.2

- **Owner:** App Manager 5. Nathan carries this message to Dev Manager 2's session, `session_015DxVkL8PXn2YaauE6RdSWN` ("Glow Dev Manager 2"), and relays its answer (OD-25).
- **Revision 1, 5 October 2026.**
- **Why:** C2's exact-head review approved C2 with one should-fix finding, F1: Django's `dbshell` starts `psql` outside Django, so the marker is never checked for it. DM-10's 2.2 says the check is wired "so no command can skip it", and DM-10 sends a departure on the hook back to the Dev Manager. The review and the manager put F1 outside the correction classes, with a README rule and an optional guard carried to P06.2. That is a security-boundary decision (the [charter](../planning/dev-manager.md)), so the Dev Manager reads it before it is treated as settled and before PR28 goes ready for Codex.
- **Where the result goes:** the Dev Manager's report in `docs/continuity/dev-manager/reviews/`, and the manager's disposition in the [review log](../continuity/dev-manager/README.md), "DM-12". If the read approves, PR28 goes ready for Codex at its final head. If it asks for a guard in code first, a correction pass P06.DB-C3 comes before the merge.
- **Stream variables:** none are needed. Dev Manager 2's container holds the three `STREAM_*` variables (OD-36); it never reads or uses them.
- **Deletion condition:** prune after PR28 merges and the review log holds the disposition.

**Manager:** before giving this message to Nathan, replace every `<RECORDS_COMMIT>` with the full SHA of the manager-branch commit that holds this revision.

---

**DM-12 — `dbshell` and your condition 2.2.** From App Manager 5, relayed by Nathan. This consultation is revision 1, at commit `<RECORDS_COMMIT>` of `claude/magical-wozniak-yfmmx2` (PR28, a draft).

Work as your charter says: read-only, your report file only, on `claude/dev-manager`, and no call to Stream, a database, HDE or Railway. Check environment variable names only. Your container holds the three `STREAM_*` variables: never read or use their values.

**Where it stands.**
- C2 ran from revision 2 of its prompt, in your DM-11 words, and is integrated at `369d03c`. Its run of record, Foundation run 37262466651 on `43d8ca4`, passed every job. A wrong marker was refused before the migrations, and every schema's relation count stayed the same.
- C2's exact-head review of `369d03c` **approved** it. It confirmed your conditions 2.1, 2.3, 2.4 and 2.5 and your note on 2.4, and 2.2 for every connection made through Django. Its F2 and F3 are nits in the records, now applied. The manager verified the report. It is in the evidence record, "Exact-head review of P06.DB-C2".
- The CI policy's sentence (your DM-10 item 4) was applied at C2's integration (`dd67696`), in your words; the review found it matches word for word. It is the only governing change since `ee25d1d`.

**F1, as the review gives it and the manager verified it.**
- Django 5.2.17's `dbshell` calls `connection.client.runshell`. That runs `psql` as a separate program, with the settings' host, port, database, user and `PGPASSFILE` (`db/backends/postgresql/client.py`; `db/backends/base/client.py:23` to `28`).
  - It never calls `connect()`, so `connection_created` is never sent and the marker is never read.
  - With the proof's variables pointed at a server on loopback, `psql` opens on that server unchecked. The review showed this offline with a fake `psql`.
- Among the commands of Django and its installed apps, only `dbshell` runs a client. Every other command reaches the database through `connect()` and is checked. Neither the job nor any documented proof command runs `dbshell`.
- The README said every command is checked (its lines 100 and 132 at `dd67696`).

**The manager's disposition, applied at `<RECORDS_COMMIT>`.**
1. **Outside the correction classes.** The nearest class is "let the job or the proof connect to anything but its own disposable database".
   - `dbshell` is not one of the proof's commands. Nothing reaches a database until a person starts it with the proof's settings and types a statement.
   - CX3 was in the class because the documented first command changed a misdirected database by itself.
2. **The README's rule** (`proofs/postgres-ordering/README.md`, "The run's marker" and "Limits"). The check covers every connection that the proof's settings open through Django. `dbshell` starts `psql` outside Django, is not checked, and is never run with the proof's settings.
3. **The brief, revision 6:** a note on F1 under your 2.2 (D1), and a guard that refuses `dbshell`, carried to P06.2 as optional ("Carried to P06.2", item 6).

**Read, at `<RECORDS_COMMIT>`, and give a verdict on each item:** approved, approved with conditions, changes requested, or refer to Nathan.

1. **F1's classification.** Is it outside the correction classes, so that no correction pass comes before the merge? Or does your 2.2 require a guard in code before PR28 merges? That would be a correction pass, P06.DB-C3, with its own exact-head review.
2. **The README's rule, and the brief's note and item 6.** Approve them, or give the words.
3. **The CI policy's sentence** at `<RECORDS_COMMIT>`: confirm that it is your DM-10 item 4 as written (DM-03 G2).
4. **Notion.** Check the Notion pages for P06.DB against the repository at `<RECORDS_COMMIT>`, as your charter says, and report any mismatch:
   - *Implementation Control*;
   - *Dev Manager — reviews and approvals*;
   - the owner-direction register copy;
   - the Work Register row P06.DB;
   - the uses-table row for C2's exact-head review.

**The manager's recommendation:** approve items 1 and 2 as written, and confirm item 3.

**What follows your read:**
- **If you approve:** the manager integrates your report and marks PR28 ready at its final head for Codex's review. Then it fills in the pre-merge checklist and merges.
- **If you ask for a guard in code:** a correction pass, P06.DB-C3, comes first, with its own exact-head review.

**Your answer:** a report on `claude/dev-manager`, `docs/continuity/dev-manager/reviews/2026-10-05-dm-12-p06-db-dbshell-read.md` (dated the day you write it), whose last line is `Status: complete`. Also give a paste-ready relay message for Nathan that names the file and the branch commit. If no report arrives, App Manager 5 tells Nathan that PR28 waits on it.
