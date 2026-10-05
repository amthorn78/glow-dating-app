# DM-10 — CX3 and the design of its correction

- **Consultation:** DM-10, revision 1, from App Manager 5, relayed by Nathan (OD-25).
- **Reviewer:** Dev Manager 2, `session_015DxVkL8PXn2YaauE6RdSWN`, branch `claude/dev-manager`.
- **Commit read:** `cd9fa03fcb62ab5279b17665865d5222434183e6`, the head of `claude/magical-wozniak-yfmmx2` (PR28, a draft again) when I fetched it. **This read covers `cd9fa03`** (DM-03 G2).
- **Environment (names only):** `STREAM_APP_ID`, `STREAM_API_KEY` and `STREAM_API_SECRET` are present, never read or used. No HDE name is present. I called no provider, database, HDE or Railway, and started no database.

## 1. What I read

**The diff `ee25d1d..cd9fa03`:**

- the brief (revision 3);
- the evidence record, "Codex's review of PR28's final head" and "Codex's second code review, of `9bcec21`", in full;
- the P11 plan's DB06 and DB09 entries;
- the proof's README;
- the mistakes log (AM5-18);
- the register's OD-17 row;
- the DM-10 consultation.

No governing file changed in that range: `AGENTS.md`, `CLAUDE.md`, `docs/pf-canon/`, the workflow, the charter and the CI policy are the same as at `ee25d1d`, which DM-09 read.

**The proof's code at `cd9fa03`, read to test the design against it:**

- `glow_ordering_proof/settings.py`, whole;
- `environment.py`, whole: the refusals, the host check at lines 108 to 112, and the Django database options;
- `concurrency.py`'s connection handling;
- `__main__.py`'s `run` server checks.

I searched the package for any connection that does not go through Django (`psycopg.connect`, `connections[...]`, `connection_created`) and found none. Every connection the proof opens is a Django connection, and each worker thread keeps one open across its tasks.

**Notion, read-only, about 01:11 UTC on 5 October:**

- *Implementation Control*, with its operating-procedure copy;
- *Dev Manager — reviews and approvals*;
- the register copy;
- the Work Register's P06.DB row.

## 2. Summary verdict

| Item | Verdict |
|---|---|
| 1 CX3's classification; correct before the merge | **Approved** |
| 2 Brief revision 3, the run's marker | **Approved with conditions** (2.1 to 2.5). Sufficient for the boundary. No simpler guard is clearly better. It weakens no DB06 or DB09 evidence, given condition 2.5 |
| 3 CX1 and CX2 carried to P06.2 | **Approved;** neither belongs in C2 |
| 4 The CI policy's database sentence | **Changes requested, narrowly:** name the marker, in the words below. Applied as written, it needs no further read |
| 5 Notion | **Matches `cd9fa03`** |

No item is Nathan's.

## 3. Findings

### Item 1 — CX3: approved, and correct it before the merge

The manager's verification matches the code:

- `connection_options` accepts `127.0.0.1`, `localhost`, `::1` or any absolute directory, and nothing else identifies the server (`environment.py:108` to `112`).
- `settings.py` builds `DATABASES` from those options at import, so `migrate` connects with them before any check that tells a disposable database from another.
- `run`'s server checks (non-superuser, `track_commit_timestamp`, isolation level) cannot tell either, and they come after `migrate` anyway.

**The class is right.** "Let the job or the proof connect to anything but its own disposable database" is exactly what a misdirected `migrate` does. The CI job is safe by construction. The package is not, and the package is what D4 and P06.2 run outside CI.

The protected boundary in `AGENTS.md` and PF01 D08 is protected by effect. A guard that rests on the operator pointing the variables correctly is the kind of guard AM5-18 records as the brief's own mistake.

**Before the merge is right.** Merging puts the documented `migrate` command on `main`, where:

- P06.2's sessions iterate locally first (D4; DM-09 sharpened the R2 guard to "before P06.2's first run of the suite on any database, local or CI" for this reason);
- any session can run it.

Carrying it would leave the gap open during exactly the runs most likely to be misdirected. The cost of correcting now is one small pass, one exact-head review and one Codex round.

### Item 2 — The run's marker: approved with conditions

**Sufficient.** The threat is misdirection: a session or person pointing the proof's variables at a database that was not created for this run. A server reached that way would have to carry a database comment equal to `glow-ordering-proof:` followed by a value generated for this run. No shared, production or HDE database carries one unless someone deliberately writes it there, which is outside this guard's purpose. The check is positive evidence of provenance; loopback was not.

**It fits the code as it stands:**

- every connection is a Django connection;
- Django's connection setup runs only the connection's own session settings (autocommit and time zone) before its `connection_created` signal;
- every management command (`migrate`, `makemigrations --check`, `facts`, `run`) opens its connection before its first query.

So a check in that signal, or in the backend's connection initialization, runs before any statement that reads or changes the schema.

**A side benefit, not a replacement.** If each new database gets a new marker, a database left from an earlier run carries the old marker and is refused. That covers most of R2's reused-database risk in practice. It does not replace R2's guard, which P06.2 still lands, because an operator can reuse a marker.

**Simpler alternatives considered:**

- **A run-specific random database name**, which the proof requires by pattern. It is nearly as strong, since a misdirected server would not have that database and the connection would fail before any statement. But it still lets the proof authenticate to the wrong server, and its provenance rests on a naming convention the operator also controls.
- **Refusing a non-empty database before `migrate`.** This stops changes to a populated database but accepts any empty one.

Neither is clearly simpler or stronger. The marker as stated is the right choice; do not switch.

**Effect on evidence: none on DB06 or DB09,** provided the check runs only when a connection is created. The workers open one connection each and keep it, so the check's single `SELECT` runs before any forced case or race. It does not:

- open a transaction that writes;
- take a lock or an xid, so the commit-order oracle is unaffected;
- change the holder's pid or the blocking-pid observations.

D1 to D5 are otherwise unchanged. D3 gains one step and D4 one recipe line.

**Conditions for the C2 prompt** (2.1 to 2.4 are conditions; 2.5 is what C2's exact-head review checks):

1. **The marker's form is fixed and checked offline.**
   - `PROOF_DB_MARKER` must be exactly 32 lowercase hexadecimal characters (`secrets.token_hex(16)`). Otherwise the settings refuse at import, like the other `PROOF_DB_*` names.
   - Empty, short, padded or prefixed values are refused, and the comparison is of the whole comment string.
   - Offline tests show each refusal. Without this, an empty marker and the bare comment `glow-ordering-proof:` would match.
2. **The check is wired so no command can skip it.**
   - It is registered in a module that every management command loads: the proof's settings or the installed app's `ready`, not `__main__`.
   - It reads `shobj_description(oid, 'pg_database')` for `current_database()`. On a mismatch, or a missing or null comment, it closes the connection through Django (`connection.close()`), so the wrapper does not keep it, then raises an exception that ends the command with a non-zero status.
   - An offline test with a fake cursor shows the handler connected and refusing. The refusal names `PROOF_DB_MARKER` and never a value.
3. **The CI step proves the refusal changed nothing.** Before the migrations:
   - the step runs `migrate` with a different well-formed marker;
   - it requires a non-zero exit and the refusal message;
   - as the superuser inside the container, it checks that the proof's database has no relation in its schemas: zero rows in `pg_class` joined to `pg_namespace`, excluding `pg_catalog` and `information_schema`; in particular, no `django_migrations`.

   A step that only checks the exit code would pass if `migrate` failed for another reason after creating a table.
4. **The marker is handled like the passwords, though it is not a credential.**
   - It is generated in the credentials step and masked with `::add-mask::` as that step's first output (cheap, and it keeps logs uniform).
   - It reaches the proof only through `PROOF_DB_MARKER` on the steps that need it.
   - The README's local recipe sets it with `COMMENT ON DATABASE` right after creating the database, with a new marker for each new database. It says the marker does not replace the reused-database guard carried to P06.2.
5. **The evidence stays the same: what C2's exact-head review checks.** The new run of record shows the same plan as `ea21ac8`:
   - 55 cases, 10 controls, the same races and floors;
   - 55 of 55 passed, every control met, 0 design violations;
   - every forced wait observed with its holder.

   The review confirms from the code that the marker query runs only at connection creation, and from the log that no worker reconnected inside a race. If C2 changes any race, case, control or floor, that is a departure, and it comes back to me.

### Item 3 — CX1 and CX2: approved as carried; neither belongs in C2

- **CX1.** The reference design cannot write a misattributed row: it derives the actor from the locked session and refuses `not_a_member` (the manager's verification, `reference.py:172` to `184`). So no claim about the reference design is affected. The gap matters when another subject, the app's adapter, runs the suite, and that is P06.2's work.
- **CX2.** The oracle is stricter than the design, so at that boundary the suite can only fail, never pass falsely. No run comes near the boundary.

  DB09's limit line already states that DB09 shows the check after the locks and the refusal of a session that expires while the send waits, not a commit ordered against expiry. Settling the rule, and any move to enforcing expiry at commit, belongs with P06.2's brief, as recorded.

Keeping C2 to CX3 alone keeps its exact-head review small and its evidence comparable with `ea21ac8` (condition 2.5).

### Item 4 — The CI policy: name the marker

The sentence stays accurate after C2, but it lists the job's safeguards for the one database in CI, and the marker becomes the safeguard that ties the proof to that database. A reader of the policy should find it there.

**In `docs/operations/ci-and-branch-policy.md`, in the sentence that begins "The one database is P06.DB's",** after "keeps in files readable only by the job's user;", insert:

> every proof command refuses, before any other statement, a database whose comment is not the run's marker, a value the job generates and masks, and a step shows a wrong marker refused, with the database left without a table, before the migrations run;

If the manager applies these words as written, no further read is needed (G2). Any other wording to this governing file needs one before PR28 merges.

### Item 5 — Notion: matches `cd9fa03`

- ***Implementation Control*** names `cd9fa03`, CX3, brief revision 3 with the marker, AM5-18 and "Next: DM-10". Its procedure copy is matched to `cd9fa03`; no governing file changed since DM-09's read.
- ***Dev Manager — reviews and approvals*** has DM-09's disposition, DM-10 pending, and my session row through DM-09.
- **The register copy** is matched to `cd9fa03`. OD-17's state matches the repository's, through "after the Dev Manager reads its design (DM-10)".
- **The Work Register** has one P06.DB row, "In progress". Its text matches the repository through CX3 and "Next: DM-10".

## 4. Verdicts

| Item | Verdict |
|---|---|
| 1 | Approved: in the correction class; correct before the merge |
| 2 | Approved with conditions 2.1 to 2.4; 2.5 for C2's exact-head review |
| 3 | Approved: CX1 and CX2 stay carried to P06.2 |
| 4 | Changes requested: the sentence above, applied as written |
| 5 | Notion matches `cd9fa03` |

The C2 prompt needs no further read from me if it applies revision 3 with conditions 2.1 to 2.4 as written. A departure on the marker's form, the hook, the CI step or the suite comes back to me.

## 5. Questions for Nathan

None.

## 6. Documentation to update

- **The brief (revision 4, or the C2 prompt):** conditions 2.1 to 2.5.
- **The CI policy:** item 4's words, at C2's integration.
- **The README:** the local recipe's marker line (2.4).
- **The evidence record:** C2's section, with the new run of record and the wrong-marker step's result.
- **The review log:** DM-10's disposition.

## 7. Limits

- **No database was started.** These points come from documented behavior and are for C2 and its review to confirm:
  - Django runs nothing but session settings before `connection_created`;
  - `shobj_description` reads the database comment;
  - `COMMENT ON DATABASE` needs the owner or a superuser.
- **I did not read Django's backend source** for this read.
- **Notion:** the pages in section 1 only.
- **No scoring** (OD-15).

## 8. Relay message for Nathan to paste into App Manager 5's session

> **From Dev Manager 2 to App Manager 5 (relayed by Nathan, 5 October 2026)**
>
> DM-10 is answered on `claude/dev-manager`, in the commit that adds `docs/continuity/dev-manager/reviews/2026-10-05-dm-10-p06-db-cx3-design-read.md`. My read covers `cd9fa03`. No item is Nathan's.
>
> **1. CX3: approved.** It is in the correction class, and correcting it before the merge is right: on `main`, P06.2's local runs would inherit the gap.
>
> **2. The run's marker: approved with conditions.** It is sufficient. Every proof connection is a Django connection, so a check at connection creation precedes any schema statement. Neither a random database name nor an empty-database check is clearly better. It weakens no DB06 or DB09 evidence, because the workers keep one connection each. Conditions for C2:
> - 2.1 `PROOF_DB_MARKER` is exactly 32 lowercase hex characters, or the settings refuse; the whole comment string is compared; offline tests show each refusal.
> - 2.2 The check is registered where every management command loads it (settings or the app's `ready`). It reads `shobj_description` for `current_database()`. On a mismatch, or a missing or null comment, it calls `connection.close()` and raises a non-zero exit. The message names the variable, never the value. An offline test with a fake cursor covers it.
> - 2.3 The CI step runs `migrate` with a different well-formed marker, requires a non-zero exit and the refusal, then as the superuser checks that no relation exists outside `pg_catalog` and `information_schema`.
> - 2.4 Mask the marker as the credentials step's first output, pass it only to the steps that need it, and give the README's local recipe `COMMENT ON DATABASE` with a new marker per database. It does not replace R2's guard.
> - 2.5 For C2's exact-head review: the same plan as `ea21ac8` (55 cases, 10 controls, the same races and floors; 55/55, 0 violations, waits observed); the marker query runs only at connection creation, and no worker reconnects inside a race.
>
> **3. CX1 and CX2: approved as carried to P06.2;** neither belongs in C2.
>
> **4. The CI policy: changes requested.** In the sentence that begins "The one database is P06.DB's", after "keeps in files readable only by the job's user;", insert: "every proof command refuses, before any other statement, a database whose comment is not the run's marker, a value the job generates and masks, and a step shows a wrong marker refused, with the database left without a table, before the migrations run;". Applied as written, it needs no further read.
>
> **5. Notion** matches `cd9fa03`.
>
> The C2 prompt needs no further read if it applies revision 3 with 2.1 to 2.4 as written.

Status: complete
