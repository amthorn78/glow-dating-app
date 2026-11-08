# Current handoff — App Manager 10 (8 November 2026; P06.3's implementation prompt with Nathan)

This file only routes: the current item, what happens next and who waits on whom. Each fact lives in one home, listed in the [documentation map](../README.md); earlier handoffs are in `docs/continuity/history/`, the last as [P06.2 to its merge](history/p06-2-handoff.md).

- **Process:** Nathan's manual relay ([manager workflow](../planning/manager-workflow.md)), with the [Dev Manager](../planning/dev-manager.md) as second-layer reviewer (OD-25). Standing directions: the [owner-direction register](owner-directions.md). A new manager starts from the [start procedure](../planning/start-prompts/next-manager.md) and reads the [mistakes log](manager-mistakes.md).

## Now

- **Manager: App Manager 10**, created by App Manager 9 at Nathan's direction (OD-58), in `Glow App - No Stream`, on the manager branch `claude/magical-wozniak-yfmmx2` (its outcome branch; PR40 merged and unsubscribed; the next PR is opened from this branch when the next records or code batch needs one).
- **Never ask Nathan to perform a GitHub operation** (OD-58; AM9-10). A CI failure that seems to call for a re-run goes to the Dev Manager first (OD-32), with options that need no action from him.
- **P06.2-F is done:** merged with PR40 at `8031361` (8 November 2026; [brief](../planning/p06-2-f-mobile-hardening.md), revision 7; [record](../testing/evidence/2026-11-01-p06-2-f-mobile-hardening.md), with the merge receipt). Its prompts are pruned; links are pinned at `8031361`. View models (option (c)) are carried to before P11 serves the chat reads ([carried items](../planning/carried-to-later-items.md)).
- **Now: P06.3** (OD-49), privacy-safe notifications at fixture scope.
  - **The brief:** [revision 2](../planning/p06-3-notifications.md) applies DM-44's conditions as written ([report](dev-manager/reviews/2026-11-08-dm-44-p06-3-brief.md), integrated at `c99aa5a`), so it needs no read before the prompt. The matrix recheck is in its [record](../testing/evidence/2026-11-08-p06-3-matrix-recheck.md).
  - **The prompt:** the [implementation prompt](../ephemeral/2026-11-08-p06-3-implementation-prompt.md), revision 1, is with Nathan, for `Glow App - No Stream`.
  - **DM-44 1.3's confirmation** of the words as applied rides the next consultation.
- **The repository is public for now** (OD-51); before it goes private, Nathan tells the manager (`'ccr-**'`, M07).
- **The order** (OD-49): P06.2-F, P06.3, the server slices SV1 to SV4, then P07 to P12; P06.2-T and P07.2a where the Work Register places them, and M07, the costed list (OD-50), before P09 and P11B.
- **Done:** P00 to P05 (fixture scope), M01 to M06, P06.1, P06.DB, P06.2, P09.3a and P06.2-F ([matrix](../planning/store-legal-safety-requirements.md); OD-55).
- **Review log:** DM-01 to DM-44, with "Deferred conditions". **Linear (OD-29).** Every prompt names its environment (OD-36, OD-40, OD-43).

## Waiting checkpoint (8 November 2026, 23:22 UTC, App Manager 10)

| Who waits | On whom | For what | If nothing arrives |
|---|---|---|---|
| App Manager 10 | Nathan | The P06.3 implementation session's report | App Manager 10 asks Nathan whether the session ran |

## Next actions (App Manager 10)

1. **The P06.3 report:**
   - verify it against the pushed branch: the diff within the owned paths, reversals re-run where cheap, a search of the diff for any token value, provider term or body field, and the run of record's logs;
   - integrate it, then open P06.3's PR from the manager branch;
   - wait for Codex on the code head and on the commit that holds the exact-head review prompt (step 6);
   - write that prompt, with DM-44 9.1's threat model.
2. **Then** the server slices SV1 to SV4 (OD-49); the second A05 message before SV2's brief (the carried-items file).

**Carried follow-ups** live in their owning homes: the P06.2 brief's "Carried to later changes", the M02 brief, the P11 plan, [`carried-to-later-items.md`](../planning/carried-to-later-items.md) and the review log's "Deferred conditions".

## Branches and PRs (`git ls-remote`, 8 November 2026, 23:22 UTC)

- **Open PRs:** none. `main` is at `8031361` (PR40's merge).
- **Remote branches:** `main`, the manager branch `claude/magical-wozniak-yfmmx2` (`8bf9d8d` before this batch) and `claude/dev-manager` (`65618c1`, DM-44's report, merged into the manager branch at `c99aa5a`), each kept by the cleanup's keep-list.
