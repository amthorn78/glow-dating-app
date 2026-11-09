# Current handoff — App Manager 10 (9 November 2026; P06.3's exact-head review asked for changes; correction C1)

This file only routes: the current item, what happens next and who waits on whom. Each fact lives in one home, listed in the [documentation map](../README.md); earlier handoffs are in `docs/continuity/history/`, the last as [P06.2 to its merge](history/p06-2-handoff.md).

- **Process:** Nathan's manual relay ([manager workflow](../planning/manager-workflow.md)), with the [Dev Manager](../planning/dev-manager.md) as second-layer reviewer (OD-25). Standing directions: the [owner-direction register](owner-directions.md). A new manager starts from the [start procedure](../planning/start-prompts/next-manager.md) and reads the [mistakes log](manager-mistakes.md).

## Now

- **Manager: App Manager 10**, created by App Manager 9 at Nathan's direction (OD-58), in `Glow App - No Stream`, on the manager branch `claude/magical-wozniak-yfmmx2` (its outcome branch; PR40 merged and unsubscribed; the next PR is opened from this branch when the next records or code batch needs one).
- **Never ask Nathan to perform a GitHub operation** (OD-58; AM9-10). A CI failure that seems to call for a re-run goes to the Dev Manager first (OD-32), with options that need no action from him.
- **P06.2-F is done:** merged with PR40 at `8031361` (8 November 2026; [brief](../planning/p06-2-f-mobile-hardening.md), revision 7; [record](../testing/evidence/2026-11-01-p06-2-f-mobile-hardening.md), with the merge receipt). Its prompts are pruned; links are pinned at `8031361`. View models (option (c)) are carried to before P11 serves the chat reads ([carried items](../planning/carried-to-later-items.md)).
- **Now: P06.3** (OD-49), privacy-safe notifications at fixture scope.
  - **The brief:** [revision 2](../planning/p06-3-notifications.md) applies DM-44's conditions as written ([report](dev-manager/reviews/2026-11-08-dm-44-p06-3-brief.md), integrated at `c99aa5a`), so it needs no read before the prompt. The matrix recheck is in its [record](../testing/evidence/2026-11-08-p06-3-matrix-recheck.md).
  - **Implemented:** code head `9c4fef5`, records `7775bba` ([record](../testing/evidence/2026-11-09-p06-3-notifications.md)); run of record 42540179430, all eight jobs passed. The manager verified it and fast-forwarded the manager branch.
  - **PR41** is open. **The exact-head review** (prompt revision 2 at `481562f`) asked for changes: F-1 (Codex's F-C1, confirmed) and F-2, both should-fix; nits F-3 to F-5 ([record](../testing/evidence/2026-11-09-p06-3-notifications.md), "Exact-head review of P06.3").
  - **Correction C1** (F-1, F-2, F-3): the [prompt](../ephemeral/2026-11-09-p06-3-c1-correction-prompt.md), revision 1, goes to Nathan after Codex completes on the commit that holds it. F-4 is carried to SV4 and F-5 to P09.
  - **DM-44 1.3's confirmation** of the words as applied rides the next consultation.
- **The repository is public for now** (OD-51); before it goes private, Nathan tells the manager (`'ccr-**'`, M07).
- **The order** (OD-49): P06.2-F, P06.3, the server slices SV1 to SV4, then P07 to P12; P06.2-T and P07.2a where the Work Register places them, and M07, the costed list (OD-50), before P09 and P11B.
- **Done:** P00 to P05 (fixture scope), M01 to M06, P06.1, P06.DB, P06.2, P09.3a and P06.2-F ([matrix](../planning/store-legal-safety-requirements.md); OD-55).
- **Review log:** DM-01 to DM-44, with "Deferred conditions". **Linear (OD-29).** Every prompt names its environment (OD-36, OD-40, OD-43).

## Waiting checkpoint (9 November 2026, 01:49 UTC, App Manager 10)

| Who waits | On whom | For what | If nothing arrives |
|---|---|---|---|
| App Manager 10 | Codex, then Nathan | Codex's review of C1's prompt commit; then C1's report | After 60 minutes with no Codex result, the manager posts `@codex review` once (step 6) |

## Next actions (App Manager 10)

1. **C1's prompt:** give it to Nathan once Codex has completed on its commit, with every finding handled.
2. **C1's report:** verify it and integrate it; then the delta review if its non-test lines are 60 or fewer (step 6), after Codex.
3. **Then** the merge (step 7), and the server slices SV1 to SV4 (OD-49).

**Carried follow-ups** live in their owning homes: the P06.2 brief's "Carried to later changes", the M02 brief, the P11 plan, [`carried-to-later-items.md`](../planning/carried-to-later-items.md) and the review log's "Deferred conditions".

## Branches and PRs (`git ls-remote`, 8 November 2026, 23:22 UTC)

- **Open PRs:** none. `main` is at `8031361` (PR40's merge).
- **Remote branches:** `main`, the manager branch `claude/magical-wozniak-yfmmx2` (`8bf9d8d` before this batch) and `claude/dev-manager` (`65618c1`, DM-44's report, merged into the manager branch at `c99aa5a`), each kept by the cleanup's keep-list.
