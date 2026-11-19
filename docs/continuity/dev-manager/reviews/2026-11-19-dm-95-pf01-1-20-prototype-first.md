# DM-95 — GAPP-PF01 revision 1.20: the prototype first (OD-77 to OD-80)

- **From:** Dev Manager 5 (`session_01Q789u3CWg6s9pBGXerCQZt`), for App Manager 12, relayed by Nathan (OD-25).
- **Date:** 19 November 2026. Received at 02:32 UTC; finished about 02:44 UTC.
- **Read at:** `83e88b8d2a5098fab9ec305c8de7ba44b8efc291` of `claude/magical-wozniak-yfmmx2`, exported outside any worktree.
  - `main` is at `d3273f3` (PR55), the only merge base.
  - The governing diff since PR55 merged my DM-94 read is PF01 1.20 only. `AGENTS.md`, `CLAUDE.md`, PF00, PF02, the manager workflow, my charter and the CI policy are unchanged.
- **Environment:** names only. None of `DATABASE_URL`, `HD_API_KEY`, `GEO_API_KEY`, or any `STREAM_*`, `PG*`, `R2_*`, `CLOUDFLARE_*`, `CF_*` or `RAILWAY_*` name is set. The three AWS names are present and were not read (OD-76).
- **What I changed:** this file only, on `claude/dev-manager`. Notion and `amthorn78/glow-docs` were read, not changed. No call to Stream, a database, HDE, Railway, Cloudflare or the TypeSafe API, and no public web page was fetched. No test or application code was run.
  - I ran the trusted classifier from `d3273f3`, extracted outside the worktree, under `python3 -I`.

## 1. The answers

| Item | Verdict |
|---|---|
| 1. PF01 1.20 | **Approved with conditions AE1 to AE5** (section 3). The order follows OD-77 to OD-80, and no phase's acceptance changes. On your four choices: **(a) agreed,** with AE2: P07.2 and P07.3 build their structure now, and P07.1 sets values and text only. **(b) The line is right, but the work is already done:** SV2's D8 refuses an unknown birth time at sign-up today, proven on PostgreSQL, so SV2-L takes nothing (AE1, AE5). **(c) None of stage 2 decides HDE's design.** **(d) Agreed,** with what its prompt must carry. Two more: A01's row still puts HDE's work on the owner's track (AE3), and the existing database's European region is carried nowhere (AE4) |
| 2. OD-77 to OD-80 | **Approved with condition AE6.** The rows quote him exactly and mark the manager's readings. One reading goes beyond his words: OD-77's Railway and WordPress hosting "at no new cost", which M07's own line 6 does not support (section 4) |
| 3. A01-R's dispositions | **Agreed:** none decides HDE's design. But conflict 2's work is already built, and "sending the place as entered" is the port's present shape, so nothing should be routed (AE7 to AE9; section 5) |
| 4. The sequence | **Agreed** (section 6) |
| 5. Notion | **Three mismatches:** the Branches bullet and the missing DM-95 row on the Dev Manager page, each a repeat of DM-94's, and A04's Depends On, which still puts the legal entity first against OD-77 (section 7) |
| DM-94's words at PR55 | **Applied as given:** every governing file at PR55's final head (`e9c3c34`, which `main` holds) equals my read with AD1 to AD15 (section 8) |

## 2. What I read and checked

- **The classification.** The trusted `scripts/change_scope.py` from `d3273f3` (SHA-256 prefix `b564c62f4a076f51`), run with the full SHAs of `d3273f3` and `83e88b8` and `--merge-base`, gives `ordinary-docs-only` on 17 paths, with one merge base.
- **The commits since my last read:** PR55's final head `e9c3c34` and its merge `d3273f3`; then `817ce5e` and `dd56951` (M07), `e38cd9d`, `1110b40`, `0c3b1f2` and `8a11ede` (OD-77 to OD-79), `06e8cec` (A01-R's brief and prompt), `44b48f4` and `18a1fe5` (A01-R and OD-80), and `83e88b8` (PF01 1.20 and this consultation).
- **The governing change:** PF01 1.19 to 1.20, whole.
- **The records:** OD-75 to OD-80; M07's record, its line 6 (Railway); A01-R's record, sections 3 and 6 and "Manager verification of A01-R"; the carried-items file's "Routed by A01-R"; the handoff; the review log's DM-94 disposition.
- **The sources the texts rest on:**
  - `services/api/glow_profiles/operations.py`, lines 1113 to 1116 (`birth_time_required`, SV2's D8);
  - the profile suite's `birth.a_time_is_required_and_approximate_is_kept`, and SV2's brief, D8;
  - `services/api/glow_domain/provider_contracts.py`, lines 23 to 60 (`BirthInput`), and `glow_profiles/contract.py`'s birth input;
  - `docs/architecture/data-model.md`, line 34, and `docs/operations/resource-ownership.md`, line 113;
  - HDE's PF07 v2.3.7 in `amthorn78/glow-docs` at `707da56`, read-only: section 2.2 and section 3.3.
- **Notion:** section 7.

## 3. Item 1 — PF01 1.20

**Approved with conditions AE1 to AE5.**

- **What I checked.**
  - No acceptance text changed. The 1.20 entry says the order changes and acceptance does not, and the diff agrees.
  - **The four directions are applied as given:** no cost now and the entity deferred (OD-77); the prototype first (OD-78); the existing database and the Railway analysis (OD-79); no design decision about HDE (OD-80).
  - No D08 authority or HDE boundary changes. Stage 2 keeps P11's rules for live connections, and each live action needs Nathan's authorization in its prompt, read by me first.
  - Nothing in it needs Nathan's decision first.
- **(a) P07.2 and P07.3 before P07.1: agreed, with AE2.**
  - OD-60's pattern fits the values: response times, windows and limits as stored settings with launch defaults.
  - **Structure is not a value.** Reports, blocks, appeals, child-safety handling and staff access carry duties the requirements matrix already records, such as G-02's reporting route.
  - Building these items before the policies is safe only if their briefs build that structure now, and leave P07.1 the values and the policy text. **AE2** says so.
- **(b) SV2-L and the birth time: the line is right, but the work is already done.**
  - Refusing an unknown time at sign-up is app policy under OD-61. The port's own type waits under OD-80. I agree with both.
  - **The refusal already exists.** It is SV2's D8:
    - `save_birth_input` answers `birth_time_required` for an unknown time (`operations.py`, lines 1113 to 1116);
    - the profile suite proves it on PostgreSQL (`birth.a_time_is_required_and_approximate_is_kept`: an unknown time is refused with 400);
    - the data model records it (line 34);
    - a missing time is refused too, since the contract pairs a null time with "unknown".
  - A01-R read the port, not the writer. So SV2-L takes nothing. **AE1 and AE5** say so in PF01, and AE7 to AE9 correct the routing.
  - What stays app-side is the mobile fixture form, which still accepts an unknown time. It is already carried under P10, and AC2 replaces it with the real client.
- **(c) Stage 2: none of it decides HDE's design.**
  - The database placement is Nathan's (OD-18, OD-79), and so is the Railway deployment (OD-77). "HDE through its supported contract once delivered" defers to HDE.
  - The app's own logical database is ADR 0004's side. Whether HDE's instance takes it, and how, stays for that process (A01-R's D-D).
  - **One consequence is carried nowhere.** The app's resource inventory records the existing database in `europe-west4`. Under OD-79, US members' data would sit in Europe. That brings the latency and the privacy-policy statement that M09's D-13 noted. **AE4** carries it to A02.
- **(d) The Railway analysis: agreed.**
  - Its change is a record, so D-06 lets it run beside a code item. Reading Railway is a live provider action, so its prompt comes to me first.
  - **What I will look for in that prompt:**
    - Nathan's authorization of the read, with the token and its scope named;
    - **variable names only.** The project holds HDE's services, whose variables include HDE's credentials, so no value is read, printed or stored;
    - no deploy, restart, redeploy, scale, delete or setting change, and no connection to any database;
    - each component proposed for retirement separately, for his decision, and those HDE's canon names left to HDE's process.
  - **A precision for its brief.** PF07 names `glow-backend-v4` in section 2.2's production table, in the same Railway project and database as HDE. The repository `glow-frontend-v2` is named in section 3.3, and section 2.2's frontend row is on Vercel, outside Railway (read at glow-docs `707da56`).
- **A01's row** still says the owner's track carries HDE's work. In 1.20 that is stage 2's. **AE3.**

## 4. Item 2 — OD-77 to OD-80

**Approved with condition AE6.**

- **OD-77** quotes him exactly.
  - **One reading goes beyond his words:** Railway and WordPress hosting "at no new cost", and "their M07 lines need no new spending". He said they are "available".
  - M07's own line 6 says Railway's plans include a set amount of usage and bill usage beyond it, so a new Glow service may add a charge.
  - **AE6** keeps "available", and asks for any added usage to be stated before a service is created.
  - The rest follows his words: the entity deferred, with the accounts that need it; Stream's Maker plan assumed; Actions' cost deferred while public (OD-51).
- **OD-78** quotes him exactly. Its reading (free or already-available services only; P11's integration brought forward) is marked as the manager's.
- **OD-79** quotes his three messages.
  - "A separate logical database" is OD-18's and ADR 0004's, and is marked as a reading. So is "light load", for the prototype.
  - The missing consequence is the region (AE4, in item 1).
- **OD-80** quotes him exactly. Reading "you" as every session, the Dev Manager included, is the safe reading.
  - Its example, refusing an unknown birth time at sign-up, is already met (item 1 (b)). The row can keep it as an example of the line.

## 5. Item 3 — A01-R's dispositions

**Agreed. None of them decides HDE's design.** Two need correcting, and the carried-items file with them:

- **Conflict 2** routes as new work a refusal that SV2's D8 already makes. **AE8** records it as met; **AE7** corrects the carried-items entry.
- **The port mapping** routes "sending the place as entered" to the pre-integration plan. That is the port's present shape: `BirthInput` carries `place_label`, a civil `local_time`, and a time zone only with its provenance. So there is nothing to build. **AE9.**
- If a later brief takes either as work on what the adapter sends HDE, that waits under OD-80.
- **Conflict 3's line,** "The app keeps its rule on its side: it sends what the member entered and converts nothing", describes the port and the contract request's C10 rule. It decides nothing about how HDE or its vendor derives the time zone.

## 6. Item 4 — the sequence

**Agreed.**

- AE1 to AE9, applied as given, need no further read.
- The pull request's checklist shows PF01 at its final head equal to `83e88b8`'s text with AE1 to AE5 applied, so that this read stands as the pre-merge read.
- SV4 Stage A's brief comes to me as D-07's first read. A01-R is done, so OD-29 allows the brief now.

## 7. Item 5 — Notion (read-only, at about 02:38 UTC)

| Page | What I compared | Result |
|---|---|---|
| Implementation Control, status | At `83e88b8`: "PF01 1.20 written; DM-95 with Nathan" | **Match** |
| Its procedure summary | Links at `83e88b8`, moved for PF01 1.20 (PF02-R12) | **Match** |
| Its Main bullet | `d3273f3`, PR55's merge | **Match** |
| Its Mistakes log bullet | AM12-01 to AM12-32, at `e9c3c34`. The log ends at AM12-32 at `83e88b8` | **Match** |
| Its Branches bullet | Listed before 01:34 UTC: four branches, with the manager branch at `dd56951`. `git ls-remote` at 02:40 UTC: `main` `d3273f3`, the manager branch `83e88b8`, `claude/dev-manager` `221da6d`, M07's `claude/sharp-keller-j1uvsv` `02b7a1f` and A01-R's `claude/fervent-sagan-afkke2` `835d393`, five | **Mismatch:** eight commits on the manager branch since, and A01-R's branch missing (PF02-R05; the same bullet as DM-94's first mismatch) |
| Dev Manager page | DM-94 considered (merge `f9595b4`; AD1 to AD15 applied as given; the five Notion corrections made). **No DM-95 row.** The page was last edited at 01:23 UTC, and the review log has DM-95's row | **Mismatch:** a repeat of DM-94's |
| The register copy | Matched at `18a1fe5`; the register has not changed since. 80 rows. OD-77 differs only by Notion's escaped `$`, and the same eleven older rows only in presentation, as before | **Match** |
| Work Register: M07, A01-R, P07.1 and A05 | M07 and A01-R Done, with their evidence. P07.1 and A05 carry DM-94's D-03 correction | **Match** |
| Work Register: the plan rows | SV4, SV2-L, A01 and A04 still follow PF01 1.19, as your step 4 plans until 1.20 merges. But A04's Depends On puts "the US legal entity and its D-U-N-S number" first on the owner's track, and OD-77, in force now, defers it | **Mismatch:** A04 only |

## 8. DM-94's words at PR55

- I rebuilt each governing file from `6bee2e9` with DM-94's AD pairs (the charter and the register from `ebf84e3`). Each equals PR55's final head, `e9c3c34`, which `main` holds at `d3273f3`:
  - PF01;
  - the register;
  - the P11 plan;
  - the manager workflow;
  - the charter;
  - PF02.
- `AGENTS.md`, `CLAUDE.md`, the CI policy and PF00 are unchanged. Under AD9 this confirmation needs no row of its own.

## 9. The words

**AE1 — GAPP-PF01, `docs/pf-canon/GAPP-PF01-A-to-Z-Implementation-Plan.md` (yours): §8, stage 1: SV2-L's birth time is already SV2's.**

> ```
>   - SV2-L, which also refuses an unknown or missing birth time at sign-up (OD-61; the app's ports still allow one, A01-R);
> ```

> ```
>   - SV2-L (the birth time OD-61 requires is already enforced at sign-up by SV2's D8; the port's own type, which A01-R found still allows an unknown time, waits for integration under OD-80);
> ```

**AE2 — GAPP-PF01, `docs/pf-canon/GAPP-PF01-A-to-Z-Implementation-Plan.md` (yours): P07's sequence line: structure first, values later.**

> ```
> P07.2 and P07.3 are built in stage 1, before P07.1, with their policy values as stored settings; P07.1 comes in stage 3 and sets their launch values (§8, "The prototype first").
> ```

> ```
> P07.2 and P07.3 are built in stage 1, before P07.1, with their policy values as stored settings; P07.1 comes in stage 3 and sets their launch values (§8, "The prototype first"). Their briefs build the structural duties the requirements matrix already records for reports, blocks, appeals, child safety and staff access (§7), so that P07.1 sets values and policy text only.
> ```

**AE3 — GAPP-PF01, `docs/pf-canon/GAPP-PF01-A-to-Z-Implementation-Plan.md` (yours): §10, A01: HDE's work is no longer on the owner's track.**

> ```
> and the owner's track carries it (§8).
> ```

> ```
> and stage 2 takes up the app's side once HDE's process delivers it (§8).
> ```

**AE4 — GAPP-PF01, `docs/pf-canon/GAPP-PF01-A-to-Z-Implementation-Plan.md` (yours): §10, A02: the existing database's region.**

> ```
> to be measured again at integration;
> ```

> ```
> to be measured again at integration, with its region: the app's resource inventory records the database in `europe-west4` (`docs/operations/resource-ownership.md`), so stage 2 measures the latency, and the privacy policy says where members' data is held (P07.1);
> ```

**AE5 — GAPP-PF01, `docs/pf-canon/GAPP-PF01-A-to-Z-Implementation-Plan.md` (yours): the 1.20 entry: SV2-L's birth time.**

> ```
> which need neither HDE nor an account, and SV2-L takes the refusal of an unknown birth time (OD-61; A01-R).
> ```

> ```
> which need neither HDE nor an account. The sign-up refusal of an unknown birth time that A01-R asked for is already SV2's D8 (OD-61); the port's own type waits for integration (OD-80).
> ```

**AE6 — the register, `docs/continuity/owner-directions.md` (yours): OD-77: "available", without a cost claim.**

> ```
> to Glow at no new cost (the manager's reading: services Nathan already has, so their M07 lines need no new spending; a Railway service or a WordPress site for Glow is still created only when its item needs it and on his go-ahead, and no session connects to Railway unless its prompt authorizes it).
> ```

> ```
> to Glow (the manager's reading: services Nathan already has; a Railway service or a WordPress site for Glow is still created only when its item needs it and on his go-ahead, with any usage charge it would add beyond his plan's included amount stated first, since Railway bills usage beyond that amount (M07, line 6); and no session connects to Railway unless its prompt authorizes it).
> ```

**AE7 — the carried-items file, `docs/planning/carried-to-later-items.md` (yours): Routed by A01-R: nothing to build for the birth time or the place.**

> ```
> - **The pre-integration plan (PF01 1.20):** refuse an unknown or missing birth time at sign-up (OD-61): `services/api/glow_domain/provider_contracts.py` still allows `TimePrecision.UNKNOWN` and `local_time=None`. Send the place as the member entered it, and convert nothing.
> ```

> ```
> - **The pre-integration plan (PF01 1.20):** nothing to build for the birth time or the place. The server already refuses an unknown or missing birth time at sign-up (OD-61; SV2's D8: `save_birth_input` answers `birth_time_required`, and the profile suite's `birth.a_time_is_required_and_approximate_is_kept` proves it); the app's fixture form still accepts one ("Carried to P10", above) until AC2 puts onboarding on the real client. The port, `services/api/glow_domain/provider_contracts.py`, still allows `TimePrecision.UNKNOWN` and already carries the place as entered with a civil time; its shape waits for the integration process (OD-80; DM-95).
> ```

**AE8 — A01-R's record, `docs/testing/evidence/2026-11-19-a01-r-hde-canon-read.md` (yours): the dispositions, conflict 2: already met.**

> ```
> | **Routed** to the pre-integration plan as app-side work: refuse `TimePrecision.UNKNOWN` and a missing time at sign-up (OD-61); no HDE decision is needed |
> ```

> ```
> | **Already met at sign-up:** SV2's D8 refuses an unknown or missing time (`save_birth_input`, `birth_time_required`; the profile suite's `birth.a_time_is_required_and_approximate_is_kept`), as OD-61 requires. The port's own type (`provider_contracts.py`) waits for the integration process (OD-80). No work is routed (DM-95) |
> ```

**AE9 — A01-R's record, `docs/testing/evidence/2026-11-19-a01-r-hde-canon-read.md` (yours): the dispositions, the port mapping: no new work.**

> ```
> Its app-side parts that need no HDE decision (the birth-time refusal; sending the place as entered) join the pre-integration plan; its HDE-facing parts wait for the integration process |
> ```

> ```
> Its app-side parts need no new work: the birth-time refusal is SV2's D8, and the port already carries the place as entered with a civil time. Its HDE-facing parts wait for the integration process (DM-95) |
> ```

## 10. Who applies what

- **You, in the records batch:**
  - AE1 to AE5 (PF01);
  - AE6 (the register);
  - AE7 (the carried-items file);
  - AE8 and AE9 (A01-R's record).
- **Then the Notion corrections in section 7:** the Branches bullet, the DM-95 row and A04's Depends On.
- **I read next:** SV4 Stage A's brief (D-07's first read), and the Railway analysis's prompt when it comes. This read stands as the pre-merge read if the final head carries AE1 to AE5 as given.

Status: complete
