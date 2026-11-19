# Nathan's direction: glow-frontend-v2 is deprecated

- **Source:** Nathan Amthor, in Dev Manager 5's session on 19 November 2026, answering DM-95's report (`04a738c`).
- **Consultation ID:** none. This is owner input.
- **Read at:** `main` at `d3273f3`; the manager's branch `claude/magical-wozniak-yfmmx2` at `83e88b8`, its head unchanged since DM-95; glow-docs at `707da56`, read only.

## The direction, word for word

> "glow-frontend-v2 is a deprecated component. make note"

DM-95 had said, on choice (d) (the Railway analysis; its section 3 and its relay message), that `glow-frontend-v2` is on Vercel, outside Railway.

## What it changes

1. **Its status.** `glow-frontend-v2` is deprecated. The app's records that keep it for a purpose are now history. ADR 0001 kept it ("Preserve, including its business/legal landing page") because its landing page presented Glow's services, support and business policies.
2. **Its old purpose already has a home.** WordPress is "the public sales landing page, the public policy and support site" (PF01 §1; OD-19). Nothing the app plans depends on the deprecated repository. At `83e88b8`, only Markdown records name it, no code does, and nothing in this repository names its domain.
3. **The Railway analysis (OD-79).** It is hosted on Vercel, not Railway (PF07 §2.2 and §4.3), and OD-79 names "the existing railway components". So the analysis does not cover it. One caution stays:
   - ADR 0001 records, from its source, that its `vercel.json` sends `/api/(.*)` to `glow-backend-v4`'s production URL, and that its live configuration and traffic were not inspected.
   - So its deprecation alone does not show that `glow-backend-v4` has no caller.
   - The analysis prompt, which comes to me first (DM-95), should say so.
4. **The app does not change HDE's canon.** PF07 still names it (§2.2, §3.3, §4.3 and §5.3), and its §6.2 records `glowme.io` as Glow's production domain, "hosted and registered at **Vercel**". That text changes only in HDE's process (D08; OD-80).
5. **Not decided, and nothing waits on it now:**
   - whether its Vercel deployment stays up, and when it is retired. Retiring it would follow PF01 §3's rule, "Retirement is separate work": a recorded retirement candidate, with its consumers, backup, rollback, DNS and data-retention consequences, carried to an explicit decision;
   - what happens to `glowme.io`, which PF07 says it serves. The app's records never name that domain, and M07's costed list still lists "A domain and WordPress hosting" as one item (line 40). P07.3's brief, when written, should say which domain the public site uses, as Nathan decides. Under OD-77 nothing is bought now.

## What the manager should update

The exact words follow. Each was checked against its file at `83e88b8`: an old passage occurs exactly once before the change, and each new passage exactly once after it. Applied as given, they need no further read.

**AF1 — the owner-direction register, `docs/continuity/owner-directions.md`: a new last row, after OD-80.** OD-81 is the next number at `83e88b8`. Replace `<commit>` with the commit the relay message names, as OD-61's row names its note's commit.

> ```
> | OD-81 | 19 Nov 2026 | In Dev Manager 5's session, after DM-95's report said that `glow-frontend-v2` is on Vercel, outside Railway (recorded word for word in `docs/continuity/dev-manager/reviews/2026-11-19-owner-direction-glow-frontend-v2-deprecated.md`, `<commit>`): *"glow-frontend-v2 is a deprecated component. make note"* | In force. **`glow-frontend-v2` is deprecated.** The Dev Manager's reading: no app work depends on it or changes it, and it is not part of the system that stage 2 integrates (OD-78). ADR 0001 kept it for its business and legal landing page; that role is WordPress's (OD-19; PF01 §1). It is hosted on Vercel, not Railway, so the Railway analysis (OD-79) does not cover it. HDE's canon still names it (PF07 §2.2, §3.3, §4.3 and §5.3); that text changes only in HDE's process (D08; OD-80). Not decided: its Vercel deployment, its retirement (separate work under PF01 §3), and the domain `glowme.io` that PF07 says it serves | ADR 0001, "Later direction"; the Railway analysis item in `docs/planning/carried-to-later-items.md` |
> ```

**AF2 — the same file, its fourth bullet (directions given in the Dev Manager's session).**

> ```
> OD-59, OD-61 and OD-65; DM-25 4.2
> ```

> ```
> OD-59, OD-61, OD-65 and OD-81; DM-25 4.2
> ```

**AF3 — ADR 0001, `docs/adr/0001-isolated-application-foundation.md`: a new section before `## Decision`, on the pattern of its "P03 placement supersession" note.** Insert it, followed by one blank line, immediately before the line `## Decision`, the only line that is exactly that.

> ```
> ## Later direction: `glow-frontend-v2` deprecated
>
> On 19 November 2026 Nathan recorded that `glow-frontend-v2` is a deprecated component (OD-81). Its "Preserve" disposition below, and the section "Existing frontend has consumers and a separate purpose to preserve", are history. The role of its business and legal landing page is now WordPress's: the public sales landing page and the public policy and support site (OD-19; PF01 §1). No app work depends on the repository or changes it. This note changes nothing in `glow-frontend-v2` or its Vercel deployment, and decides nothing about its retirement, which is separate work (PF01 §3).
> ```

**AF4 — the carried-items file, `docs/planning/carried-to-later-items.md`: the Railway analysis item.**

> ```
> - **The Railway analysis item (OD-79):** PF07 §2.2 names `glow-backend-v4` (Railway, the same project and database) and `glow-frontend-v2` (Vercel) as Glow infrastructure beside HDE; retiring a component that HDE's canon names is for HDE's process (D08).
> ```

> ```
> - **The Railway analysis item (OD-79):** PF07 §2.2 names `glow-backend-v4` (Railway, the same project and database) and `glow-frontend-v2` (Vercel) as Glow infrastructure beside HDE; retiring a component that HDE's canon names is for HDE's process (D08). `glow-frontend-v2` is deprecated (OD-81) and is not on Railway, so the analysis does not cover it. ADR 0001 records, from its source, that its `vercel.json` sends `/api/(.*)` to `glow-backend-v4`'s production URL, and that its live configuration and traffic were not inspected. So its deprecation alone does not show that `glow-backend-v4` has no caller.
> ```

**No change needed:**

- **A01-R's record, conflict 9's row:** routing it to the Railway analysis as an input is still right; AF4 carries the new fact.
- **`docs/planning/sources/2026-09-23-database-audit-assignment.md`, line 81:** a source record, which already calls it the "Legacy frontend repository".
- **PF01:** it does not name the repository. §3 mentions legacy frontends only as P01's inputs (the planning inventory, line 91; "P01 bounded reuse assessment", line 99). Its rule "Retirement is separate work" already covers what this direction leaves open (point 5).
- **DM-95:** what it said stays true; this note adds the status.

**The manager's own records, in its own words:**

- the review log, `docs/continuity/dev-manager/README.md`: this note as owner input (as 25 September's are recorded under "Nathan's answers and directions"), and in Dev Manager 5's Sessions row;
- the current handoff: OD-81.

## Notion (read only)

- **The register copy** gains OD-81 (OD-26).
- **The Dev Manager page** records the 25 September owner-input files; this note joins that record.
- **P01.1's Work Register row** (Done, 23 September 2026) says "Existing backend and frontend remain preserved" and "No retirement authorized or performed". It is the history of a finished item, so no change.
- **A workspace search** for `glow-frontend-v2` showed it on no other page. The search ranks by relevance, so this does not prove that no other page names it.

## Checks

- **Environment, names only:** `DATABASE_URL`, `HD_API_KEY` and `GEO_API_KEY` are not set.
- **No calls** to Stream, a database, HDE, Railway, Cloudflare or TypeSafe. Notion and glow-docs were read only.
- **The words:** every old passage above occurs exactly once at `83e88b8`, and each new passage exactly once after the change (checked by script).

Status: complete
