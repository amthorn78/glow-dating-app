# DM-11 — The C2 prompt's one departure from DM-10

- **Consultation:** DM-11, revision 1, from App Manager 5, relayed by Nathan (OD-25).
- **Reviewer:** Dev Manager 2, `session_015DxVkL8PXn2YaauE6RdSWN`, branch `claude/dev-manager`.
- **Commit read:** `d50f334b57a26c559ccf7fea541bafe35fc3b381`, the head of `claude/magical-wozniak-yfmmx2` (PR28, a draft) when I fetched it. The prompt is `docs/ephemeral/2026-10-05-p06-db-c2-correction-prompt.md`, revision 1, 193 lines, read whole. **This read covers that commit** (DM-03 G2).
- **Environment (names only):** `STREAM_APP_ID`, `STREAM_API_KEY` and `STREAM_API_SECRET` are present, never read or used. No HDE name is present. I called no provider, database, HDE or Railway, and started no database.

## 1. What I read

- **The C2 prompt, whole.**
- **The diff `cd9fa03..d50f334`:** brief revision 4 (D1's "DM-10's conditions", D3 item 5, D4 condition 2, "Sessions"), the review log's DM-10 disposition, the register's OD-17 row, the handoff and the DM-11 consultation.
- **For item 2:** I compared the prompt's quotations of 2.1, 2.2 and 2.4 with the text of my DM-10 report, word for word.
- **Notion, read-only, about 02:01 UTC on 5 October:**
  - *Implementation Control*, matched to `d50f334`;
  - *Dev Manager — reviews and approvals*;
  - the register copy, matched to `d50f334`;
  - the Work Register's P06.DB row;
  - the uses-table row "P06.DB-C2 correction pass".

## 2. Summary verdict

| Item | Verdict |
|---|---|
| 1 The departure from 2.3 | **Approved with conditions.** The reason is right: my query was wrong. The replacement needs three precisions, given as words in section 3 |
| 2 The rest of the prompt | **Confirmed:** 2.1, 2.2 and 2.4 are quoted as written, and 2.5 is kept. No other departure. One note for the exact-head review |
| 3 Notion | **Matches `d50f334`** |

A revision 2 of the prompt that applies section 3's words as written needs no further read. No item is Nathan's.

## 3. Findings

### Item 1 — The departure from 2.3: approved with conditions

**The reason is right, and the error was mine.** My 2.3 asked for "zero rows in `pg_class` joined to `pg_namespace`, excluding `pg_catalog` and `information_schema`". Every PostgreSQL database holds the toast tables, and their indexes, for its own catalogs in the schema `pg_toast`. So that count is never zero, even in a database just created, and a step built on it would fail on every run, a good database included. The manager's reading of PostgreSQL is correct, and I should have caught it in DM-10.

**Excluding the `pg_` schemas is the right idea.**

- PostgreSQL reserves that prefix: `CREATE SCHEMA` refuses a name that starts with `pg_` unless the server runs with `allow_system_table_mods`, which the job does not set.
- So no role, and no Django migration, can put a relation into an excluded schema directly. Any table `migrate` creates lands in `public` or another user schema and is counted. Only its toast table would land in `pg_toast`, and the main table is counted anyway.

**Three precisions make it exact.**

1. **The prefix test must be literal.** In SQL, `LIKE 'pg_%'` treats `_` as a wildcard, so it also excludes a schema named `pgx`, which a role can create. The prompt says "whose name starts with `pg_`". The query must test exactly that: `NOT starts_with(n.nspname, 'pg_')`, available since PostgreSQL 11, or `n.nspname NOT LIKE 'pg\_%'`.
2. **The query must run in the proof's database.** `pg_class` is per database. Run from the `postgres` database, the check would pass whatever `migrate` did to `glow_proof`. The step runs `psql` with `-d` naming the proof's database.
3. **Compare before and after, so the check does not rest on the exclusion alone.** The prompt already prints each schema's relation count before the wrong-marker `migrate`. The step takes the same per-schema count again afterwards, `pg_toast` included, and requires every count to be unchanged. This also catches a relation in an excluded schema, should one ever appear, and it shows the review exactly what the exclusion leaves out.

**Words for the prompt** (section 3, item 3; they replace the departure's two bullets):

> - **The one departure, which DM-11 approved with these words.** Every PostgreSQL database keeps the toast tables of its own catalogs in the schema `pg_toast`, so the query as quoted counts PostgreSQL's relations even in a new database. The step therefore runs, as the superuser inside the container and with `psql -d` naming the proof's database (never `postgres`), a count of `pg_class` rows joined to `pg_namespace` per schema, before and after the wrong-marker `migrate`. It requires:
>   - every schema's count after equals its count before, `pg_toast` included;
>   - the count over every schema except `information_schema` and those for which `starts_with(nspname, 'pg_')` is true is zero, before and after;
>   - `to_regclass('public.django_migrations')` is null after.
>
>   The step prints both per-schema tables once. It prints no name of a role, password or marker.

### Item 2 — The rest of the prompt: confirmed

- **2.1, 2.2 and 2.4** are quoted in section 3, items 1, 2 and 4, word for word as DM-10 wrote them. The prompt's additions are within them:
  - `PROOF_DB_MARKER` among the proof's names, with the exact expected comment;
  - the "nothing before it but session settings" rule;
  - the offline tests listed case by case;
  - the comment set from the file the role step already reads, so that nothing prints the statement;
  - the removal of any file that holds the marker;
  - every other job and the gate byte-identical.
- **2.5** is the prompt's "The evidence stays the same", with the stop-and-report rule for any change to a race, case, control, floor or the reference design.
- The start gate (with AM5-15's stale-prompt checks), the narrow "fix here only if" classes, the D4 local-run rules, the wait-before-pushing rule (AM5-14), the owned paths and the report are consistent with the brief and with DM-08 to DM-10.
- **No other departure.**

**One note for C2's exact-head review, not a departure.** 2.4 says the marker reaches the proof "only through `PROOF_DB_MARKER` on the steps that need it". In GitHub Actions, that means:

- each step that needs the marker reads it from the job's protected temporary directory into the variable for its own commands;
- never through `$GITHUB_ENV`, which would hand it to every later step, the upload step included;
- never through a step output (`$GITHUB_OUTPUT`), which the runner withholds once the value is masked.

The review checks this in the workflow diff.

### Item 3 — Notion: matches `d50f334`

- ***Implementation Control*** is matched to `d50f334` and names brief revision 4, the C2 prompt (revision 1) and DM-11.
- ***Dev Manager — reviews and approvals*** has DM-10's disposition, matching the review log, and DM-11 pending. My session row runs through DM-10, merged at `2152463`.
- **The register copy** is matched to `d50f334`. OD-17's state matches the repository word for word through "reads the C2 prompt's one departure from them before it runs (DM-11)".
- **The Work Register** has one P06.DB row, "In progress". Its text matches through "Next: DM-11".
- **The uses table**'s row "P06.DB-C2 correction pass" matches the prompt header:
  - Opus 5.5 at high, score 1.92, confidence 0.79;
  - the six rung probabilities;
  - Fable 5.1 0.01, Opus 5.5 0.99;
  - sent at 2026-10-05T01:58:22Z;
  - Nathan's pick pending.

## 4. Verdicts

| Item | Verdict |
|---|---|
| 1 | Approved with conditions: the words in section 3 replace the departure's two bullets |
| 2 | Confirmed; one note for the exact-head review |
| 3 | Notion matches `d50f334` |

**Revision 1 should not run as it is.** Its query could be satisfied from the wrong database, and its prefix test is a wildcard. Run a revision 2 that applies section 3's words as written; it needs no further read (G2).

## 5. Questions for Nathan

None.

## 6. Documentation to update

- **The C2 prompt (revision 2):** section 3, item 3, replaced by the words above.
- **The brief, D1's "manager's note" under 2.3:** a pointer to DM-11.
- **The review log:** DM-11's disposition. Note there that DM-10's 2.3 query was the Dev Manager's error, caught by the manager.

## 7. Limits

- **No database was started.** These facts are from PostgreSQL's documented behavior, and C2's run shows them:
  - the catalog toast tables in `pg_toast`;
  - the `pg_` reservation;
  - `starts_with`;
  - `to_regclass`;
  - per-database `pg_class`.
- **Notion:** the pages in section 1 only.
- **No scoring** (OD-15).

## 8. Relay message for Nathan to paste into App Manager 5's session

> **From Dev Manager 2 to App Manager 5 (relayed by Nathan, 5 October 2026)**
>
> DM-11 is answered on `claude/dev-manager`, in the commit that adds `docs/continuity/dev-manager/reviews/2026-10-05-dm-11-p06-db-c2-prompt-read.md`. My read covers `d50f334`. No item is Nathan's.
>
> **1. The departure: approved with conditions.** You are right: my 2.3 query was wrong, because every database's catalog toast tables sit in `pg_toast`. Excluding the reserved `pg_` schemas is right, with three precisions:
> - the prefix test must be literal (`starts_with(nspname, 'pg_')`; `LIKE 'pg_%'` is a wildcard);
> - the query runs in the proof's database (`psql -d` naming it, never `postgres`);
> - the per-schema counts before and after the wrong-marker `migrate` must be identical, `pg_toast` included.
>
> Replace the departure's two bullets in section 3 item 3 with:
>
> "- **The one departure, which DM-11 approved with these words.** Every PostgreSQL database keeps the toast tables of its own catalogs in the schema `pg_toast`, so the query as quoted counts PostgreSQL's relations even in a new database. The step therefore runs, as the superuser inside the container and with `psql -d` naming the proof's database (never `postgres`), a count of `pg_class` rows joined to `pg_namespace` per schema, before and after the wrong-marker `migrate`. It requires: every schema's count after equals its count before, `pg_toast` included; the count over every schema except `information_schema` and those for which `starts_with(nspname, 'pg_')` is true is zero, before and after; and `to_regclass('public.django_migrations')` is null after. The step prints both per-schema tables once. It prints no name of a role, password or marker."
>
> **2. The rest: confirmed.** 2.1, 2.2 and 2.4 are quoted word for word, 2.5 is kept, and there is no other departure. A note for C2's exact-head review: the marker reaches each step from the job's temporary directory, never via `$GITHUB_ENV` or a step output.
>
> **3. Notion** matches `d50f334`, the uses-table row included.
>
> Run a revision 2 with these words, not revision 1. Applied as written, it needs no further read.

Status: complete
