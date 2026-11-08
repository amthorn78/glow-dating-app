# Current handoff — App Manager 10 (8 November 2026; P06.2-F merged; P06.3 next)

This file only routes: the current item, what happens next and who waits on whom. Each fact lives in one home, listed in the [documentation map](../README.md); earlier handoffs are in `docs/continuity/history/`, the last as [P06.2 to its merge](history/p06-2-handoff.md).

- **Process:** Nathan's manual relay ([manager workflow](../planning/manager-workflow.md)), with the [Dev Manager](../planning/dev-manager.md) as second-layer reviewer (OD-25). Standing directions: the [owner-direction register](owner-directions.md). A new manager starts from the [start procedure](../planning/start-prompts/next-manager.md) and reads the [mistakes log](manager-mistakes.md).

## Now

- **Manager: App Manager 10**, created by App Manager 9 at Nathan's direction (OD-58), in `Glow App - No Stream`, on the manager branch `claude/magical-wozniak-yfmmx2` (its outcome branch; PR40 merged and unsubscribed; the next PR is opened from this branch when the next records or code batch needs one).
- **Never ask Nathan to perform a GitHub operation** (OD-58; AM9-10). A CI failure that seems to call for a re-run goes to the Dev Manager first (OD-32), with options that need no action from him.
- **P06.2-F is done:** merged with PR40 at `8031361` (8 November 2026; [brief](../planning/p06-2-f-mobile-hardening.md), revision 7; [record](../testing/evidence/2026-11-01-p06-2-f-mobile-hardening.md), with the merge receipt). Its prompts are pruned; links are pinned at `8031361`. View models (option (c)) are carried to before P11 serves the chat reads ([carried items](../planning/carried-to-later-items.md)).
- **Next: P06.3** (OD-49), named to Nathan before it starts; its brief goes to the Dev Manager where the charter requires. DM-43's deferred confirmations (C7's prompt, its words, 4.1's text) ride the next consultation.
- **The repository is public for now** (OD-51); before it goes private, Nathan tells the manager (`'ccr-**'`, M07).
- **The order** (OD-49): P06.2-F, P06.3, the server slices SV1 to SV4, then P07 to P12; P06.2-T and P07.2a where the Work Register places them, and M07, the costed list (OD-50), before P09 and P11B.
- **Done:** P00 to P05 (fixture scope), M01 to M06, P06.1, P06.DB, P06.2, P09.3a and P06.2-F ([matrix](../planning/store-legal-safety-requirements.md); OD-55).
- **Review log:** DM-01 to DM-43, with "Deferred conditions". **Linear (OD-29).** Every prompt names its environment (OD-36, OD-40, OD-43).

## Waiting checkpoint (8 November 2026, 18:49 UTC, App Manager 10)

| Who waits | On whom | For what | If nothing arrives |
|---|---|---|---|
| Nobody | — | P06.2-F is merged; App Manager 10 names P06.3 to Nathan and writes its brief | — |

## Next actions (App Manager 10)

1. **P06.3:** name it to Nathan (OD-49), read its plan entry and the carried items it owns, write its brief, and take it to the Dev Manager where the charter requires, with DM-43's deferred confirmations in the same consultation.
2. **Then** the server slices SV1 to SV4 (OD-49); the second A05 message before SV2's brief (the carried-items file).

**Carried follow-ups** live in their owning homes: the P06.2 brief's "Carried to later changes", the M02 brief, the P11 plan, [`carried-to-later-items.md`](../planning/carried-to-later-items.md) and the review log's "Deferred conditions".

## Branches and PRs (`git ls-remote`, 8 November 2026, 18:49 UTC)

- **Open PRs:** none. `main` is at `8031361` (PR40's merge).
- **Remote branches:** `main`, the manager branch `claude/magical-wozniak-yfmmx2` (`7feba0d`, PR40's head, merged) and `claude/dev-manager` (`3a1c6a0`, merged), each kept by the cleanup's keep-list. Cleanup run 42511605823 deleted the eight P06.2-F session branches, each merged into `main`.
