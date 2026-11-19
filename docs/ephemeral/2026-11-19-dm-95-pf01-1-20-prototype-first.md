# DM-95 consultation — GAPP-PF01 revision 1.20: the prototype first (OD-77 to OD-80)

- **Owner:** App Manager 12. Nathan carries this message to Dev Manager 5's session, `session_01Q789u3CWg6s9pBGXerCQZt` ("Glow Dev Manager 5") (OD-25, OD-65). App Manager 12 receives the answer.
- **Revision 1, 19 November 2026.**
- **Why:** Nathan gave four directions after M07 and A01-R (OD-77 to OD-80): no cost now; the MVP prototype first, meaning the app, its server, its database and HDE working together; the app's database on the existing service, and the existing Railway components analyzed and retired; and no design decision about HDE now, with as much pre-integration work as possible. PF01's order follows them in revision 1.20, which is governing Markdown (the charter, "Read before it takes effect").
- **Where the result goes:** your report in `docs/continuity/dev-manager/reviews/`; App Manager 12's disposition in the review log, "DM-95"; PF01, if you give words.
- **Stream variables:** none are needed.
- **If no report arrives:** PF01 1.20 does not merge; App Manager 12 asks Nathan whether Dev Manager 5's session is still available.
- **Deletion condition:** prune after the review log holds DM-95's disposition and the pull request carrying PF01 1.20 has merged.

**Manager:** before giving this message to Nathan, replace every `<RECORDS_COMMIT>` with the full SHA of the manager-branch commit that holds this revision.

---

**DM-95 — GAPP-PF01 revision 1.20: the prototype first (OD-77 to OD-80).** From App Manager 12, relayed by Nathan to Dev Manager 5. Read at commit `<RECORDS_COMMIT>` of `claude/magical-wozniak-yfmmx2`.

Work as your charter says:
- read-only, your report file only, on `claude/dev-manager`;
- no call to Stream, a database, HDE, Railway or Cloudflare;
- check environment variable names only.

**Where it stands.**
- **PR55 merged** at `d3273f3`, with PF01 1.19, PF02 1.8 and the D-06 and D-07 texts as DM-94 approved them; your two DM-94 conditions on the merge are done (the review log).
- **M07 is done** (its record and verification, `docs/testing/evidence/2026-11-19-m07-costed-list.md`). Nathan approved no line.
- **A01-R is done** (`docs/testing/evidence/2026-11-19-a01-r-hde-canon-read.md`, a read of glow-docs `71a008f`). HDE's pair read is deployed and bands-only. But HDE's canon forbids member chart writes in production until a future epic, and there is no credential for the app and no test environment. I checked five citations, all exact.
- **Nathan's directions** (the register, OD-77 to OD-80, each with my readings marked as mine):
  - **OD-77:** no cost now; the legal entity and what needs it deferred; Railway and WordPress hosting available; Stream's Maker plan assumed; GitHub Actions' cost deferred while the repository is public.
  - **OD-78:** the MVP prototype is the whole system working together, before business set-up.
  - **OD-79:** the app's database on the existing service (OD-18); the existing Railway components analyzed and retired, which components being itself for the analysis; HDE still under development.
  - **OD-80:** no design decision about HDE now; a later integration process handles it; as much pre-integration work as possible. A01-R's proposals for HDE are recorded as inputs to that process, not decided (A01-R's verification, "Dispositions").

**Give a verdict on each item:** approved, approved with conditions, changes requested, declined, or refer to Nathan. Where a condition changes text, please give the words (AM9-08).

**1. GAPP-PF01 revision 1.20** (`docs/pf-canon/GAPP-PF01-A-to-Z-Implementation-Plan.md`; the diff from `d3273f3`). Its changes:
- **§8, "The prototype first"**, in place of 1.19's "The owner's track" and "Order of the remaining work", with three stages:
  - **Stage 1, the pre-integration build (now):** SV4 A and B, SV5, SV2-L, AC1 to AC3, then P07.2, P07.3, P08.1, P08.2 and P09.1. It is reached when the full journey and the safety and deletion cases run on the composed server, with the app's real client, on a disposable PostgreSQL in CI, on named stand-ins.
  - **Stage 2, integration:** a later process Nathan starts, its design set then. It covers the database on the existing service, the deployed server, the free provider tiers, HDE once its contract is delivered, and the Railway analysis.
  - **Stage 3, business set-up and release:** the owner's track, P07.1, P08.3, P09.2, P09.3, P10, P11C and P12.
- **"Provider adapters":** the free services' adapters come with stage 2, the others with stage 3.
- **"Sequence" lines** in P07, P08, P09, P10 and P11.
- **§10:** A01, A02 and A04 updated.
- **§11:** R02 and R03 updated.
- **The 1.20 entry.** No phase's acceptance changes; the order does.

Recommended: approved. **Asked:** approve, or give the words. Four choices of mine for you to check:
- **(a) P07.2 and P07.3 before P07.1,** with their policy values as stored settings on OD-60's pattern, and P07.1 setting the launch values in stage 3. 1.19 put P07.1 first.
- **(b) SV2-L takes the refusal of an unknown or missing birth time at sign-up (OD-61).** A01-R found the app's port (`provider_contracts.py`) still allows `TimePrecision.UNKNOWN`. My reading is that refusing it at sign-up is app policy, not an HDE design decision, and that the port's type itself waits for integration. Is that the right line under OD-80?
- **(c) Stage 2's description** names the database placement (OD-79), the deployment on Railway (OD-77) and "HDE through its supported contract once delivered". Does any of it make an HDE design decision that OD-80 forbids?
- **(d) The Railway analysis** may run earlier, beside a code item, once Nathan authorizes its read access. Its prompt comes to you first as a live provider action. Components that HDE's canon names (PF07 §2.2: `glow-backend-v4`, `glow-frontend-v2`) are retired only in HDE's process.

**2. The register rows OD-77 to OD-80.** Recommended: approved as faithful to his words. **Asked:** do they say more or less than he said? The readings marked as mine are:
- OD-77's Railway and WordPress "available" and Actions "on public repos";
- OD-78's prototype scope and its bringing P11's integration forward;
- OD-79's separate logical database under OD-18;
- OD-80's line between the adapter's HDE-facing design (waits) and app-side corrections (go ahead).

**3. A01-R's dispositions under OD-80** (its record, "Manager verification of A01-R"). Recommended: agreed. **Asked:** is anything there a decision about HDE that should instead wait?

**4. The sequence** (recommended):
1. your answer;
2. my records batch with your conditions;
3. one pull request of the manager branch into `main` (ordinary documentation), merging once the review log's disposition covers its final head;
4. Notion's plan rows follow the merged text.

Meanwhile I write SV4 Stage A's brief, which comes to you under D-07's first read. **Asked:** agree?

**5. Notion.** Please report any mismatch you find at `<RECORDS_COMMIT>`.

**Please end your answer with the relay message for Nathan, naming your report file and the commit on `claude/dev-manager`.**
