# Current handoff — App Manager 10 (8 November 2026; P06.2-F, DM-43)

This file only routes: the current item, what happens next and who waits on whom. Each fact lives in one home, listed in the [documentation map](../README.md); earlier handoffs are in `docs/continuity/history/`, the last as [P06.2 to its merge](history/p06-2-handoff.md).

- **Process:** Nathan's manual relay ([manager workflow](../planning/manager-workflow.md)), with the [Dev Manager](../planning/dev-manager.md) as second-layer reviewer (OD-25). Standing directions: the [owner-direction register](owner-directions.md). A new manager starts from the [start procedure](../planning/start-prompts/next-manager.md) and reads the [mistakes log](manager-mistakes.md).

## Now

- **Manager: App Manager 10**, created by App Manager 9 at Nathan's direction (OD-58), in `Glow App - No Stream`, on the manager branch `claude/magical-wozniak-yfmmx2` (its outcome branch; PR40 stays), subscribed to PR40.
- **Never ask Nathan to perform a GitHub operation** (OD-58; AM9-10). A CI failure that seems to call for a re-run goes to the Dev Manager first (OD-32), with options that need no action from him.
- **Now: P06.2-F**, the mobile hardening ([brief](../planning/p06-2-f-mobile-hardening.md), revision 6; [record](../testing/evidence/2026-11-01-p06-2-f-mobile-hardening.md)), in PR40. C1 to C5 are verified and integrated (C4's code through C5's run; [DM-41](../continuity/dev-manager/reviews/2026-11-08-dm-41-p06-2-f-c4-run-failure.md)).
- **Correction C6 is done and integrated** (code head `6913cc0`, merged at `80383d8`; runs 42494621474 and 42498252005 green): [DM-42](../continuity/dev-manager/reviews/2026-11-08-dm-42-p06-2-f-c5-review-findings.md)'s comment-only words. Its delta review asked for changes: a form at a rest parameter's place passes (F-1; the record, "Delta review of correction C6"). **In flight: [DM-43](../ephemeral/2026-11-08-dm-43-p06-2-f-c6-review-finding.md)**, carried by Nathan to Dev Manager 4 (DM-42 5.3); no correction prompt before its answer.
- **The repository is public for now** (OD-51); before it goes private, Nathan tells the manager (`'ccr-**'`, M07).
- **The order** (OD-49): P06.2-F, P06.3, the server slices SV1 to SV4, then P07 to P12; P06.2-T and P07.2a where the Work Register places them, and M07, the costed list (OD-50), before P09 and P11B.
- **Done:** P00 to P05 (fixture scope), M01 to M06, P06.1, P06.DB, P06.2 and P09.3a ([matrix](../planning/store-legal-safety-requirements.md); OD-55).
- **Review log:** DM-01 to DM-43, with "Deferred conditions". **Linear (OD-29).** Every prompt names its environment (OD-36, OD-40, OD-43).

## Waiting checkpoint (8 November 2026, 16:28 UTC, App Manager 10)

| Who waits | On whom | For what | If nothing arrives |
|---|---|---|---|
| App Manager 10 | Nathan carrying DM-43 to Dev Manager 4 | Dev Manager 4's DM-43 report, relayed | Ask Nathan whether Dev Manager 4's session is still available |

## Next actions (App Manager 10)

1. **On DM-43's answer:** apply it; if a correction follows (C7), write its prompt with its TypeSafe reading, after Codex on the commit that holds it.
2. **Then** C7's review on DM-43's terms, the pre-merge checklist, the merge and its receipt.
3. **Then** P06.3 and the slices, each named to Nathan before it starts (OD-49); the second A05 message before SV2's brief (the carried-items file).

**Carried follow-ups** live in their owning homes: the P06.2 brief's "Carried to later changes", the M02 brief, the P11 plan, [`carried-to-later-items.md`](../planning/carried-to-later-items.md) and the review log's "Deferred conditions".

## Branches and PRs (`git ls-remote`, 8 November 2026, 16:28 UTC)

- **Open: PR40** (P06.2-F), from the manager branch. `main` is at `bac3c19`.
- **Kept, by the cleanup's keep-list:** `main`, the manager branch, and `claude/dev-manager` (`b338ea2`, merged into the manager branch).
- **In PR40's item, all merged into the manager branch:** `claude/practical-wozniak-fg1e2i` (`02f1972`), `claude/trusting-cori-gxlila` (`0e98f25`), `claude/inspiring-ramanujan-tjpril` (`3c0acfe`), `ccr-7506019b-5rfdfn` (`14e37a6`), `claude/upbeat-mccarthy-499h9k` (`691dfba`, C4) `claude/inspiring-ride-chqpjx` (`e4f9728`, C5) and `claude/charming-albattani-o8i1cb` (`e0910c7`, C6); the cleanup deletes each once PR40 merges into `main`.
