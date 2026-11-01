# DM-36 consultation — `noxcturnal` at M06's head, before PR38 merges

- **Owner:** App Manager 8. Nathan carries this message to Dev Manager 3's session, `session_01KVuPEpFRh9B22beZKTKb27` ("Glow Dev Manager 3"), and relays its answer (OD-25).
- **Revision 1, 1 November 2026.**
- **Why:** M06 stage two's exact-head review found two facts about `noxcturnal` that bear on DM-35 section 8's acceptance. DM-35 asked for any change in those facts to come to it first, and the review asks for both to reach the Dev Manager before the merge.
- **Where the result goes:** your report in `docs/continuity/dev-manager/reviews/`; the manager's disposition in the [review log](../continuity/dev-manager/README.md), "DM-36"; then PR38's merge checklist.
- **Stream variables:** none are needed.
- **If no report arrives:** PR38 does not merge. The manager asks Nathan whether the session is still available.
- **Deletion condition:** prune after the review log holds DM-36's disposition and PR38 has merged.

**Manager:** before giving this message to Nathan, replace every `<RECORDS_COMMIT>` with the full SHA of the manager-branch commit that holds this revision.

---

**DM-36 — `noxcturnal` at M06's head, before PR38 merges.** From App Manager 8, relayed by Nathan. This consultation is revision 1, at commit `<RECORDS_COMMIT>` of `claude/magical-wozniak-yfmmx2`.

Work as your charter says: read-only, your report file only, on `claude/dev-manager`, and no call to Stream, a database, HDE or Railway. Check environment variable names only.

**Where it stands.**
- **M06 stage two is done.** Expo SDK 58.0.22, code head `524d42f`, is in [PR38](https://github.com/amthorn78/glow-dating-app/pull/38). Its run of record, 41310128518, and the PR run on `95b07d8`, 41312699119, both passed all eight jobs, with the rendered suite at 97 of 97. The advisories left are `glob` and `minimatch` (moderate, tooling), smaller than OD-54's list.
- **The exact-head review** of `524d42f` (prompt revision 1 at `95b07d8`) would approve the code on code and security grounds. It found all 170 added or changed lock entries matching the registry, the type fix emitting identical JavaScript, no test weakened, and every guard allowing what it did on SDK 57. Its verdict, "changes required", is for the records only. The stage-two record's "Exact-head review of stage two" holds it, with a disposition for each finding.
- **Its finding 1** (should fix; a record claimed more than the code):
  - The record, and DM-35 section 8's "Where it runs", said `noxcturnal`'s native addon runs at bundle time in CI and in sessions. **At this head nothing loads it.** `@expo/cli` 58.1.18 turns the native transform worker on only when the app config sets `experiments.noxcturnalTransformWorker` (`instantiateMetro.js:268-269`); `app.config.ts:37` sets only `typedRoutes`; and `@expo/metro-config` 58.0.20 requires `noxcturnal` lazily on that path only.
  - The reviewer's preload logger saw no addon load and no `noxcturnal` require during a full `export:development`.
  - The manager confirmed the gate in the published packages and corrected the record, marked.
  - The reviewer's view: the risk is lower than recorded, but if anyone turns the experiment on, an unattested native binary starts running, and that change should come back to review.
- **Its finding 2** (should fix; for you):
  - `noxcturnal` 0.1.11, like 0.1.9 and 0.1.10, was published by GitHub Actions through npm's trusted publishing (`npm-oidc-no-reply@github.com`), with no provenance attestation.
  - The reviewer, from memory and unverified here: npm generates provenance automatically when trusted publishing runs from a public repository. If that holds, the missing attestation suggests a private source repository or provenance switched off, which bears on DM-35's reason that "its repository is in Expo's organization".
  - The stage-two record raised this as "one precision for the Dev Manager", and the manager's verification did not route it (AM8-18).
- **The nits:** `expo`'s own `expo-modules` `bin` and the moved `expo-internal` (finding 3), and `expo-modules-macros` 0.27.1 against DM-35's 0.30.0 (finding 4), are applied in the record. The failed-reset landing (finding 6), with two optional assertions (finding 5), is carried to P06.2-F, E11.

**Read, at `<RECORDS_COMMIT>`:**
- `docs/testing/evidence/2026-11-01-m06-sdk-58-upgrade.md`: the new-package review's table and its `noxcturnal` block, "Limits", "Manager verification of stage two" and "Exact-head review of stage two";
- your DM-35, section 8;
- the carried-items file's "Carried to P06.2-F";
- the review log's "Deferred conditions".

**Give a verdict on each item:** approved, approved with conditions, changes requested, declined, or refer to Nathan.

1. **`noxcturnal`'s acceptance.** On finding 1 (installed, not executed at this head) and finding 2 (trusted publishing without provenance), does DM-35 section 8's acceptance stand for the merge?
2. **A standing condition.** Should enabling `experiments.noxcturnalTransformWorker`, or any change that makes the build load `noxcturnal`'s addon, come to you first and be named in that change's exact-head review? If so, where should it live: the review log's "Deferred conditions", `apps/mobile/AGENTS.md`, or both? A governing file would need your read in its own PR.
3. **The records corrections:** do the record's marked corrections (findings 1, 3 and 4) say what the code and the registry show?
4. **The carried landing** (findings 5 and 6, to E11): is carrying them right, given that the guards' allowances are unchanged and the reset screen stays unreachable?
5. **The merge:** may PR38 merge after your disposition, the PR run and Codex's review on its final head, and the advisory list confirmed against OD-54?

**Reply** with your report's path and your `claude/dev-manager` commit, in a relay message for Nathan.
