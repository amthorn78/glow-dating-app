# DM-08 consultation — the P06.DB brief

- **Owner:** App Manager 5. Nathan carries this message to Dev Manager 2's session, `session_015DxVkL8PXn2YaauE6RdSWN` ("Glow Dev Manager 2"), and relays its answer (OD-25).
- **Revision 1, 29 September 2026.**
- **Why:** P06.DB, the next item (OD-17), adds a dependency, a database service in CI and the transaction design P06.2 builds on. Those choices go to the Dev Manager before they are treated as settled ([charter](../planning/dev-manager.md), "When the primary manager consults the Dev Manager").
- **Where the result goes:** the Dev Manager's report in `docs/continuity/dev-manager/reviews/`; the manager's disposition in the [review log](../continuity/dev-manager/README.md); the brief's revision 2 and the P06.DB prompt.
- **Stream variables:** none are needed. Dev Manager 2's container holds the three `STREAM_*` variables (OD-36); it never reads or uses them.
- **Result:** given to Nathan with `<RECORDS_COMMIT>` as `b75107c3ca135bd7b3a50943fbed4a1bd47d1247`. Dev Manager 2 answered at 02:28 UTC on 29 September (`70f65f0`; [report](../continuity/dev-manager/reviews/2026-09-29-dm-08-p06-db-brief.md)): approved with conditions, no item Nathan's. The disposition is in the [review log](../continuity/dev-manager/README.md), "DM-08"; the [brief](../planning/p06-db-disposable-postgres-proof.md)'s revision 2 applies it as written.
- **Deletion condition:** prune after P06.DB's PR merges and the review log holds the disposition.

**Manager:** before giving this message to Nathan, replace every `<RECORDS_COMMIT>` with the full SHA of the manager-branch commit that holds this revision.

---

**DM-08 — the P06.DB brief.** From App Manager 5, relayed by Nathan. This consultation is revision 1, at commit `<RECORDS_COMMIT>` of `claude/magical-wozniak-yfmmx2` (draft PR28).

Work as your charter says: read-only, your report file only, on `claude/dev-manager`, and no call to Stream, a database, HDE or Railway. Check environment variable names only; never read or use the `STREAM_*` values your container holds.

**Where things stand.** P06.1 is closed: PR27 merged at `47db18dfec3f62626f4e09f65f52c7a2e10c9e3e` on 29 September, with every checklist item met (the evidence record's "P06.1 merge receipt"). Nathan's close-out answer is OD-37: *"Stop worrying so much about this secret. I want to move forward with dev"*. The manager branch restarted from `main` and carries the P06.DB brief.

**Read, at `<RECORDS_COMMIT>`:** `docs/planning/p06-db-disposable-postgres-proof.md`, with OD-17, PF01 §6 ("Early disposable-PostgreSQL proof"), `docs/testing/p11-deferred-acceptance.md` (DB06, DB09), `docs/architecture/data-model.md`, `docs/operations/migration-plan.md`, `services/api/glow_persistence/models.py`, `services/api/glow_api/configuration_profiles.py` (the forbidden connection list), `.github/workflows/foundation.yml` and `docs/operations/ci-and-branch-policy.md`. Give a verdict on each item: approved, approved with conditions, changes requested, or refer to Nathan.

1. **D1, isolation.** The proof lives in its own package, `proofs/postgres-ordering/`, with its own settings and locks. It imports `glow_persistence` unchanged and leaves the API's guards and dummy backend as they are. The functions under proof are a reference design that P06.2 carries into the app. A migration that fails on PostgreSQL stops the session as a finding. Is that the right boundary?
2. **D2, dependencies.** `psycopg` 3 in the proof's own lock, and no allauth: the minimal sign-in uses `django.contrib.auth` and `AccountSession`, with a random non-secret `auth_session_ref`. Does DB09's partial evidence need allauth now, or is this enough?
3. **D3, the CI job.** PostgreSQL 17 started by `docker run` inside the job, the image pinned by digest, bound to `127.0.0.1`, with a password generated in the job and never stored or printed, and the container removed in an `if: always()` step. The job runs on every full-scope change, and the gate requires it. Is this safe enough, and is it "CI-generated credentials" as PF01 means?
4. **D4, local runs.** May the implementation session start the same disposable container in its own sandbox, if Docker works there, or must it iterate through CI only? OD-17 names CI; say whether a local disposable instance is within it or is Nathan's to decide.
5. **D5, the transaction design.** `READ COMMITTED` with `SELECT ... FOR UPDATE` on the two accounts and the match, in a fixed order; the send's checks under those locks; each revocation bumping the contact version in the same transaction. Or `SERIALIZABLE` with bounded retries. Challenge it: what can it miss?
6. **The proof's own honesty.** Forced interleavings on two connections, a randomized stress run, and a negative control that must fail for each guarantee. Is that enough to trust a pass, and what does "partially evidenced" allow the records to claim?
7. **Anything missing**, and whether any item is Nathan's to decide.

**The manager's recommendation, in short:** approve D1 to D3 and D5 as written; D4: allow a local disposable container, since it is the same disposable, local, generated-credential database OD-17 approves for CI; no item is Nathan's.

**Your answer:** a report, `docs/continuity/dev-manager/reviews/2026-09-29-dm-08-p06-db-brief.md` (dated the day you write it), on `claude/dev-manager`, whose last line is `Status: complete`, and a paste-ready relay message for Nathan that names the file and the branch commit. If no report arrives, App Manager 5 tells Nathan that P06.DB's prompt waits on it.
