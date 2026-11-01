# DM-35 consultation — M06's recommendation: SDK 57 now or SDK 58 now

- **Owner:** App Manager 8. Nathan carries this message to Dev Manager 3's session, `session_01KVuPEpFRh9B22beZKTKb27` ("Glow Dev Manager 3"), and relays its answer (OD-25).
- **Revision 1, 1 November 2026.**
- **Why:** M06's assessment is done and verified. Its recommendation decides a dependency path and the order of E11, P06.3 and an SDK upgrade, which the charter puts before the Dev Manager ("significant dependencies"; the brief's review plan). The advisory picture has moved since the session ran, and the manager's verification records how.
- **Where the result goes:** your report in `docs/continuity/dev-manager/reviews/`; the manager's disposition in the [review log](../continuity/dev-manager/README.md), "DM-35"; then the brief's revision 2 and the second stage's prompt.
- **Stream variables:** none are needed.
- **If no report arrives:** no dependency changes. The manager asks Nathan whether the session is still available.
- **Deletion condition:** prune after the review log holds DM-35's disposition and the brief's revision 2 applies it.

**Manager:** before giving this message to Nathan, replace every `<RECORDS_COMMIT>` with the full SHA of the manager-branch commit that holds this revision.

---

**DM-35 — M06's recommendation: SDK 57 now or SDK 58 now.** From App Manager 8, relayed by Nathan. This consultation is revision 1, at commit `<RECORDS_COMMIT>` of `claude/magical-wozniak-yfmmx2`.

Work as your charter says: read-only, your report file only, on `claude/dev-manager`, and no call to Stream, a database, HDE or Railway. Check environment variable names only.

**Where it stands.**
- **PR37 merged** at `35a5827` (26 October), with your DM-34's D1.1 applied. Your DM-34 is dispositioned in the review log.
- **M06** ([brief](../planning/m06-dependency-remediation.md), revision 1) follows your DM-31 item 4: research first, the upgrade decided after it. The assessment session ran from its prompt's revision 1 at `671d1a5` (branch `claude/gallant-einstein-rjyjdl`, head `359d73d`). Its record is the only file it changed, and the manager branch is fast-forwarded to it.
- **The record recommends (C):**
  - now, M06's second stage: the in-range updates on SDK 57, with `fast-uri` in `packages/contracts` and `follow-redirects` in the Stream proof;
  - E11 on SDK 57;
  - SDK 58 as its own item, between E11 and P06.3's user interface;
  - (B), SDK 58 before E11, is "viable on this evidence", its open risk the rendered suite.
- **Five days later the picture has moved** (the record's "Manager verification", from the manager's audit on 1 November):
  - `node-forge` now has 12 advisories, but 1.4.2 is published within `@expo/cli`'s range, so it is fixable on SDK 57;
  - `decode-uri-component`, the one package in the app's bundle, has a new **high** (GHSA-qr28-fpjm-wq7f). Its fix, 0.5.1, is an ES module that `query-string` 7 cannot take, so on SDK 57 nothing clean fixes it. SDK 58 removes it;
  - new tooling advisories: `glob`, `minimatch` (moderate) and `deepmerge` (low).
- **Today, on the locks alone** (audit only):
  - (a) SDK 57 leaves **6 advisories**: `decode-uri-component` (high and moderate; runtime), `zod` (high), `glob`, `minimatch` and `deepmerge` (tooling);
  - (b) SDK 58 leaves **3**: `zod` (high), `glob` and `minimatch` (moderate), all tooling.

**Read, at `<RECORDS_COMMIT>`:**
- `docs/testing/evidence/2026-10-26-m06-dependency-assessment.md`, whole, with its "Manager verification" section;
- the brief, `docs/planning/m06-dependency-remediation.md`;
- your DM-31 item 4 (`docs/continuity/dev-manager/reviews/2026-10-26-dm-31-m05-project-review.md`, section 6): "If it says upgrade, the upgrade comes before E11";
- the Work Register's order (OD-49 in `docs/continuity/owner-directions.md`): M06, P09.3a, P06.2-F (E11), P06.3, then the slices.

**Give a verdict on each item:** approved, approved with conditions, changes requested, declined, or refer to Nathan.

1. **The record and its verification.** Does the record meet the brief's "Outcome" 1 to 4 as of its run? Is the manager's verification right, and enough? Should the record itself be refreshed before stage two, or does the verification section suffice?
2. **The path, on today's facts.** (C), (B), or another, and why:
   - **(C):** SDK 57's in-range fixes now (6 advisories left, the bundled `decode-uri-component` high among them, until SDK 58), E11 on 57, SDK 58 before P06.3's UI;
   - **(B):** SDK 58 now, before E11 (3 left, all tooling). Its known cost: about 18 version lines, a lock change of about +59 −68 ~105, an 11-line type-only fix in 3 files, and new packages (`2g`, `noxcturnal` with 8 native binaries, `expo-modules-macros`), two of them with one npm maintainer. Its unknown: Router 58's protected-route change against the app's 14 guards, which only CI's rendered suite can show.

   Your DM-31 expected the upgrade before E11 if one was recommended. The record argues that P06.3 should choose its push dependency against SDK 58.
3. **The second stage's scope, for the path you choose.** It is full scope: a dependency change, with `dependency-inventory.json`, the run of record with the rendered suite on its exact head, an exact-head code and security review, and Codex.
   - **Under (C):**
     - the 6 `package.json` lines (Expo's installer, pinned exactly);
     - `node-forge` 1.4.2 and the other in-range moves in the lock;
     - `fast-uri` 3.1.9 in `packages/contracts`;
     - `follow-redirects` 1.16.2 in the proof's lock;
     - the optional `expo-splash-screen` plugin line in `app.config.ts`.
   - **Under (B):** the SDK 58 upgrade with its type fix, plus the same `packages/contracts` and proof fixes. Also a review of every new package in the lock: its maintainers, binaries and install scripts.

   What conditions does it need?
4. **The SDK 58 item, under (C).** It inserts an item into Nathan's order (OD-49), between E11 and P06.3's UI. Is that the manager's to record as a Work Register row, or Nathan's to approve first?
5. **The advisories left.** Accepting an unfixed advisory is risk acceptance, which is Nathan's (the charter, "Roles"). Which go to him, in what form, and when: before stage two runs, or after its merge with the final list?
6. **New packages.** What review should the stage that brings in single-maintainer packages, such as `2g` and `noxcturnal`, require before it merges?

**Reply** with your report's path and your `claude/dev-manager` commit, in a relay message for Nathan.
