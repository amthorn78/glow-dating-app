# DM-09 — PR28's governing read

- **Consultation:** DM-09, revision 1, from App Manager 5, relayed by Nathan (OD-25).
- **Reviewer:** Dev Manager 2, `session_015DxVkL8PXn2YaauE6RdSWN`, branch `claude/dev-manager`.
- **Commit read:** `ee25d1d3deaef4b3d73b97f7f9012ed7208dbc3c`, the head of `claude/magical-wozniak-yfmmx2` (draft PR28) when I fetched it. `main` is `47db18dfec3f62626f4e09f65f52c7a2e10c9e3e`. **This read covers `ee25d1d`** (DM-03 G2).
- **Environment (names only):** `STREAM_APP_ID`, `STREAM_API_KEY` and `STREAM_API_SECRET` are present, never read or used. No HDE name is present. I called no provider, database, HDE or Railway.

## 1. What I read

**The governing diff, `47db18d..ee25d1d`.**

- Seven commits touch the two files: `8651652`, `541ec99`, `4511bbc`, `82c3883`, `fcc4992`, `cbb3ff7` and `ee25d1d`.
- The diff is 11 lines added and 7 removed.
- `AGENTS.md` and `CLAUDE.md` at every level, `docs/pf-canon/` and the charter are unchanged in that range.

**Checked against the code it describes:** the CI policy against `.github/workflows/foundation.yml` at `ee25d1d`. I read the whole "Database proof checks" job and the gate.

**Also read at `ee25d1d`:**

- for DM-07's carried items: `CLAUDE.md`, the charter (lines 49, 80 and 100), PF01 1.11 (§4's Operations row, §7 line 236, the revision history), PF00 1.10 (line 14, the revision history), the manager workflow (line 14 and step 3) and the environment inventory;
- for item 3:
  - the evidence record's "Exact-head review of P06.DB-C1", read in full, with the report, the manager's verification, the corrections and the disposition;
  - the P11 plan's DB06 and DB09 rows and "Early partial evidence";
  - the proof README's "Limits";
  - the brief's "Carried to P06.2";
- the TypeSafe readings in the headers of the five P06.DB prompts.

**Notion, read-only, about 00:20 UTC on 5 October:**

- *Implementation Control*, last edited 00:18 UTC, including its operating-procedure copy;
- *Dev Manager — reviews and approvals* (00:18 UTC);
- the register copy (00:18 UTC);
- every Work Register row whose Work ID starts with P06.DB;
- the uses-table rows for P06.DB.

## 2. Summary verdict

| Item | Verdict |
|---|---|
| 1 The CI policy | **Approved** |
| 1 The manager workflow | **Approved.** No change adds a rule Nathan did not direct |
| 2 (a) DM-07's changes after `89a8d01` | **Confirmed as applied** |
| 2 (b) The three items left as they are | **Confirmed as they stand;** two *consider* items for the next change to those files |
| 3 C1's review dispositions | **Approved.** The guard is carried to P06.2, not landed before the merge. One *soon* wording tightening to DB09's mark |
| 4 Notion | **Matches `ee25d1d`** |

**Nothing blocks PR28's merge from my side.** No item is Nathan's.

## 3. Findings

### Item 1 — The governing Markdown

**The CI policy (`541ec99`, `4511bbc`): approved.** Every statement it adds matches the workflow at `ee25d1d`:

- **The job count and names.** Six application jobs, named in the classification paragraph, and "five before P06.DB added the sixth". The gate's `needs` is `[scope, api, mobile, smoke, artifact, proof, database]`, and its loop requires all six.
- **The database job, step by step:**
  - the hash-locked install, the offline tests under `env -i`, Ruff and mypy;
  - credentials generated with `secrets.token_hex(24)` under `set +x` and `umask 077`, and masked before anything else prints;
  - the image pinned by digest, published on `127.0.0.1:5433` only, with `track_commit_timestamp=on`;
  - a bounded readiness wait;
  - a non-superuser role, with its statement file deleted and its output withheld from the log;
  - the migrations from zero and `makemigrations --check --dry-run`;
  - the suite, the stress run, the controls and the oracle;
  - the results JSON uploaded for 14 days;
  - the `if: always()` removal of the container, its volume and the credential files, then a check that no proof container remains.
- **No credentials leak into the configuration.** There is no repository secret, and no `PG*` or `DATABASE_URL` name: the proof's own `PROOF_DB_*` names and a `passfile` are used.

  The policy's sentence on credentials changes from "No service credentials, database services… are configured in CI" to "No service credentials… are configured in CI. The one database is P06.DB's". That is accurate: the generated passwords are not service credentials, and the policy says it is not the app's database.
- **The upload pin's Node.js 20 note** (F6) describes the pin without changing it, and names its two users correctly: Mobile checks and Database proof checks (AM5-12).

  *Consider:* list "a newer upload-artifact pin" among the handoff's recorded follow-ups, so "a later change" has an owner.

**The manager workflow: approved.** Each change applies its source as written:

| Change | Source | Read |
|---|---|---|
| Notion checklist: search by Work ID before creating a row; the old-wording query looks for duplicate IDs (`8651652`) | AM5-11; DM-08 §8 | Applies DM-08's finding as written |
| Supersession sweep: run before each records commit; at a status change, read each changed document's status lines, headline first (`82c3883`) | AM5-10, AM5-13 | Applies both preventions |
| Step 3, "Say when a session may push again" (`fcc4992`) | AM5-04, AM5-14 | Correct, and consistent with the CI policy's cancel-in-progress paragraph |
| Step 3, "Make a stale prompt stop at its start gate", and the template's start-gate line (`cbb3ff7`) | AM5-15 | Correct. C1's review shows it working: a records-only commit landed during the review, the review classified it as `ordinary-docs-only` and correctly went on |
| Step 5, "Follow a stray read to every result" (`ee25d1d`) | AM5-16, AM5-17 | Correct. It generalizes R2 and R5 into a verification habit |

**No change adds a rule Nathan has not directed.** All five are the manager's own preventions, each citing its mistake entry, which OD-11 and OD-27 make the manager's responsibility. None changes what Nathan sees, decides or must do.

### Item 2 — DM-07's carried items

**(a) Confirmed as applied, each as DM-07 wrote it:**

- **`CLAUDE.md` line 16:** "created by the manager from the Dev Manager start prompt, or by its predecessor at Nathan's direction, OD-35".
- **The charter:**
  - line 49: the boundary's exception for the successor (OD-35);
  - line 100: "Succession (OD-35)" in the session lifecycle;
  - line 80: the environment, `Glow App - No Stream` for future Dev Manager sessions.
- **PF01 1.11:**
  - §7 line 236: "confirmed live by the I1 review on 25 September 2026";
  - §4 line 118: WordPress "never reads or writes app or HDE tables";
  - both in revision 1.11's history.
- **PF00 1.10, line 14:** "Nathan reinitiates managers manually or directs a manager to create its successor (OD-31)", with its revision note.
- **The manager workflow:**
  - line 14: Nathan starts each session "in the app cloud environment the prompt names (OD-36)";
  - step 3: "Every prompt names the environment to start in" (OD-36).

**(b) Confirmed as they stand:**

1. **The manager creating the Dev Manager as the usual path.** This holds in `AGENTS.md`, `CLAUDE.md`'s manager line, PF00, PF01's execution-model line and D10. It is still the usual path, and OD-35 is an exception that `CLAUDE.md`'s Dev Manager line and the charter carry. Nothing reads as forbidding what OD-35 allows.

   *Consider,* at PF01's next revision: a pointer to OD-35 in D10.
2. **`CLAUDE.md`'s "the dedicated app cloud environment".** What the sentence asserts holds for both environments: no HDE variables, and the pinned toolchain.

   The environment inventory records `Glow App - No Stream`'s Setup script as unknown. The C1 review, run there, found `python3.12` 3.12.14 at `/root/.local/bin`, which is where the bootstrap script installs it. That is good evidence the script runs there too.

   *Consider,* at the next change to `CLAUDE.md`:
   - "the app cloud environment its prompt names (OD-36)";
   - in the inventory, the No Stream environment's Setup script, once Nathan's settings page or a session confirms it.
3. **The workflow's "none added" wording** (step 3, AM3-17 and AM3-19). It is conditional ("one started while the `STREAM_*` variables were set… then says 'none added'"), so under OD-36 it applies exactly to sessions started in `Glow app`. A prompt for `Glow App - No Stream` can say "none present". No change is needed.

### Item 3 — C1's exact-head review: the dispositions

**No correction pass: agree.** R1 and R2 are limits on the evidence, not defects in what PR28 claims:

- the forced cases cover the send-first order deterministically, with the waits observed;
- the CI job starts a new database in every run, which the review saw in seven logs.

The manager confirmed R1's counts and R2's code paths independently. The one citation slip it found (`budget.py`) has no effect.

**Do the DB06 and DB09 claims exceed the runs?**

- **DB06:** no. Its claim reads "orders send authorizations against block, unmatch, suspension, deletion and sign-out… under forced and randomized races". With R1's limit in the same entry (the send-first order rests on the forced cases, with counts) and R2's (a new database per run), the entry says no more than run 36534514283 and the forced cases show.
- **DB09:** slightly, in its lead phrase, and only for a reader who stops early. The mark claims "the app-side session and epoch revocation ordering against sends". Its own limit says that the epoch check is never the deciding refusal, because every epoch bump comes with the account leaving `active`.

  **Soon (before the merge if the manager has a records batch anyway; otherwise at P06.2):** reword the lead to "the app-side session revocation ordering against sends (sign-out, expiry, and account-state revocation, which bumps the epoch); the epoch's consistency is checked but not exercised as the deciding refusal". It is a wording change in a non-governing file and needs no read.

**Should the guard land before PR28 merges? No; carry it, as the disposition says.**

- PR28's evidence cannot be affected by R2: CI always uses a new database.
- Landing the guard now would make a new code head, a new run of record and another exact-head review, for no change to any claim.

One sharpening for the P06.2 brief: "before P06.2 runs the suite against the adapter" should read "**before P06.2's first run of the suite on any database**, local or CI". The README already says a local run needs a new cluster until the guard lands. P06.2's iteration will be local first, and that is where a reused database would bite.

*Consider,* also for P06.2's brief: R3 and R4's two untested guards (the per-iteration oracle call site, and the empty-signal guard). A test for each costs little when the suite is moved onto the adapter interface.

### Item 4 — Notion: matches `ee25d1d`

- **Implementation Control:** its status names `ee25d1d`, P06.DB's sessions and C1's review result. Its operating-procedure copy carries every new workflow item, each with its cited mistake entry:
  - the Work ID search;
  - the sweep's status lines;
  - "push nothing more until the Foundation run";
  - the stale-prompt gate;
  - the stray read.
- ***Dev Manager — reviews and approvals*:** DM-08's disposition, and DM-09 pending. My session row lists DM-06 to DM-08 with their merges.
- **The register copy:** matched to `ee25d1d`. OD-17's state matches the repository word for word; OD-35 to OD-37 are present.
- **The Work Register:** one P06.DB row, "In progress". The old row no longer appears in a query of the database, so the DM-08 duplicate is resolved (AM5-11). Its text and links match the repository, including AM5-15 to AM5-17 and "Next: DM-09".
- **The uses table:** five P06.DB rows. Each matches its prompt header's score and Nathan's pick:
  - the implementation: 3.63, picked Fable 5.1 at ultracode;
  - the review: 3.93;
  - C1: 2.22;
  - C1's review revision 1: 2.81, not run;
  - C1's review revision 2: 2.82.

## 4. Verdicts

| Item | Verdict |
|---|---|
| 1 CI and branch policy | Approved |
| 1 Manager workflow | Approved |
| 2 (a) | Confirmed as applied |
| 2 (b) 1 to 3 | Confirmed as they stand |
| 3 | Approved; guard carried to P06.2's first run on any database; DB09 wording *soon* |
| 4 Notion | Matches `ee25d1d` |

This read covers `ee25d1d`. A later change to either governing file before the merge needs a new read. A records-only change elsewhere does not.

## 5. Questions for Nathan

None.

## 6. Documentation to update

- **Soon:** DB09's lead wording in the P11 plan.
- **The P06.2 brief:** the guard before P06.2's first run on any database; R3 and R4's tests (*consider*).
- **Consider:**
  - the handoff's follow-ups: the upload-artifact pin;
  - at the next change to those files: `CLAUDE.md`'s environment phrase, the inventory's No Stream Setup script, and PF01 D10's pointer to OD-35.
- **The review log:** DM-09's disposition; then the pre-merge checklist cites it.

## 7. Limits

- **No CI log read.** The run facts come from the review and the manager's verification. I checked the workflow text, not a run.
- **The image digest's PostgreSQL version** is taken from the job's own record (`SELECT version()`), not checked by me.
- **Notion:** the pages in section 1 only.
- **No scoring** (OD-15).

## 8. Relay message for Nathan to paste into App Manager 5's session

> **From Dev Manager 2 to App Manager 5 (relayed by Nathan, 5 October 2026)**
>
> DM-09 is answered on `claude/dev-manager`, in the commit that adds `docs/continuity/dev-manager/reviews/2026-10-05-dm-09-p06-db-governing-read.md`. My read covers `ee25d1d`. Nothing blocks PR28's merge from my side, and no item is Nathan's.
>
> **1. Governing Markdown.**
> - **The CI policy: approved.** Every statement matches `foundation.yml` at `ee25d1d`: six jobs and the gate's `needs`; the database job's credentials, loopback, digest, commit timestamps, non-superuser role, upload and `if: always()` cleanup. *Consider:* put the newer upload-artifact pin among the handoff's follow-ups.
> - **The manager workflow: approved.** All five changes apply their mistake entries or DM-08 as written. None adds a rule Nathan did not direct.
>
> **2. DM-07's carried items.**
> - **(a) Confirmed as applied:** `CLAUDE.md` line 16; the charter's lines 49, 80 and 100; PF01 1.11 §7 and §4; PF00 1.10; the workflow's OD-36 lines.
> - **(b) Confirmed as they stand.** *Consider,* at the next change to those files: `CLAUDE.md` "the app cloud environment its prompt names (OD-36)"; the inventory's No Stream Setup script; a PF01 D10 pointer to OD-35.
>
> **3. C1's review dispositions: approved.** No correction pass. DB06's claim stands with its limits.
> - **Soon:** DB09's lead wording slightly overstates. Reword it to "session revocation ordering against sends (sign-out, expiry, and account-state revocation, which bumps the epoch); the epoch's consistency is checked but not exercised as the deciding refusal". It needs no read.
> - **The guard:** carry it, do not land it before the merge, because PR28's CI evidence cannot be affected. Sharpen the carried item to "before P06.2's first run of the suite on any database, local or CI". *Consider:* tests for R3 and R4 there.
>
> **4. Notion** matches `ee25d1d`. The duplicate P06.DB row is resolved, and the uses table matches every prompt header.

Status: complete
