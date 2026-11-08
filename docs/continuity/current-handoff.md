# Current handoff — App Manager 10 (8 November 2026; P06.2-F, C7's review)

This file only routes: the current item, what happens next and who waits on whom. Each fact lives in one home, listed in the [documentation map](../README.md); earlier handoffs are in `docs/continuity/history/`, the last as [P06.2 to its merge](history/p06-2-handoff.md).

- **Process:** Nathan's manual relay ([manager workflow](../planning/manager-workflow.md)), with the [Dev Manager](../planning/dev-manager.md) as second-layer reviewer (OD-25). Standing directions: the [owner-direction register](owner-directions.md). A new manager starts from the [start procedure](../planning/start-prompts/next-manager.md) and reads the [mistakes log](manager-mistakes.md).

## Now

- **Manager: App Manager 10**, created by App Manager 9 at Nathan's direction (OD-58), in `Glow App - No Stream`, on the manager branch `claude/magical-wozniak-yfmmx2` (its outcome branch; PR40 stays), subscribed to PR40.
- **Never ask Nathan to perform a GitHub operation** (OD-58; AM9-10). A CI failure that seems to call for a re-run goes to the Dev Manager first (OD-32), with options that need no action from him.
- **Now: P06.2-F**, the mobile hardening ([brief](../planning/p06-2-f-mobile-hardening.md), revision 7; [record](../testing/evidence/2026-11-01-p06-2-f-mobile-hardening.md)), in PR40. C1 to C5 are verified and integrated (C4's code through C5's run; [DM-41](../continuity/dev-manager/reviews/2026-11-08-dm-41-p06-2-f-c4-run-failure.md)).
- **Correction C6 is done and integrated** (code head `6913cc0`, merged at `80383d8`; runs 42494621474 and 42498252005 green): [DM-42](../continuity/dev-manager/reviews/2026-11-08-dm-42-p06-2-f-c5-review-findings.md)'s comment-only words. Its delta review asked for changes: a form at a rest parameter's place passes (F-1; the record, "Delta review of correction C6"). [DM-43](../continuity/dev-manager/reviews/2026-11-08-dm-43-p06-2-f-c6-review-finding.md) (`3a1c6a0`, merged at `62470db`) approved comment-only words that name the compared type at each place. **Correction C7 is done and integrated** (code head `d27324b`, merged at `ed95d83`; run 42503721311 green; the record, "Manager verification of correction C7"). **In flight: [C7's delta review](../ephemeral/2026-11-08-p06-2-f-c7-review-prompt.md)**, revision 1, given to Nathan once Codex has read PR40's head, which holds it.
- **The repository is public for now** (OD-51); before it goes private, Nathan tells the manager (`'ccr-**'`, M07).
- **The order** (OD-49): P06.2-F, P06.3, the server slices SV1 to SV4, then P07 to P12; P06.2-T and P07.2a where the Work Register places them, and M07, the costed list (OD-50), before P09 and P11B.
- **Done:** P00 to P05 (fixture scope), M01 to M06, P06.1, P06.DB, P06.2 and P09.3a ([matrix](../planning/store-legal-safety-requirements.md); OD-55).
- **Review log:** DM-01 to DM-43, with "Deferred conditions". **Linear (OD-29).** Every prompt names its environment (OD-36, OD-40, OD-43).

## Waiting checkpoint (8 November 2026, 17:31 UTC, App Manager 10)

| Who waits | On whom | For what | If nothing arrives |
|---|---|---|---|
| App Manager 10 | Codex (an external party), then Nathan running C7's review | Codex on PR40's head; then the review's report, relayed | Codex: `@codex review` once after 60 minutes (OD-53); the review: nothing to chase (AM6-01) |

## Next actions (App Manager 10)

1. **On the review's report:** record it with a disposition for each finding; a form inside the changed words that evades them goes to the Dev Manager first (DM-43 3.3).
2. **Then** the Dev Manager's next consultation (DM-43's deferred: C7's prompt, its words, 4.1's text), the pre-merge checklist, the merge and its receipt.
3. **Then** P06.3 and the slices, each named to Nathan before it starts (OD-49); the second A05 message before SV2's brief (the carried-items file).

**Carried follow-ups** live in their owning homes: the P06.2 brief's "Carried to later changes", the M02 brief, the P11 plan, [`carried-to-later-items.md`](../planning/carried-to-later-items.md) and the review log's "Deferred conditions".

## Branches and PRs (`git ls-remote`, 8 November 2026, 17:31 UTC)

- **Open: PR40** (P06.2-F), from the manager branch. `main` is at `bac3c19`.
- **Kept, by the cleanup's keep-list:** `main`, the manager branch, and `claude/dev-manager` (`3a1c6a0`, merged into the manager branch).
- **In PR40's item, all merged into the manager branch:** `claude/practical-wozniak-fg1e2i` (`02f1972`), `claude/trusting-cori-gxlila` (`0e98f25`), `claude/inspiring-ramanujan-tjpril` (`3c0acfe`), `ccr-7506019b-5rfdfn` (`14e37a6`), `claude/upbeat-mccarthy-499h9k` (`691dfba`, C4) `claude/inspiring-ride-chqpjx` (`e4f9728`, C5) `claude/charming-albattani-o8i1cb` (`e0910c7`, C6) and `claude/practical-cannon-1sag8n` (`927ebbd`, C7); the cleanup deletes each once PR40 merges into `main`.
