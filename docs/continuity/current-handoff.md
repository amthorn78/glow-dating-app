# Current handoff — App Manager 10 (8 November 2026; P06.2-F, DM-41)

This file only routes: the current item, what happens next and who waits on whom. Each fact lives in one home, listed in the [documentation map](../README.md); earlier handoffs are in `docs/continuity/history/`, the last as [P06.2 to its merge](history/p06-2-handoff.md).

- **Process:** Nathan's manual relay ([manager workflow](../planning/manager-workflow.md)), with the [Dev Manager](../planning/dev-manager.md) as second-layer reviewer (OD-25). Standing directions: the [owner-direction register](owner-directions.md). A new manager starts from the [start procedure](../planning/start-prompts/next-manager.md) and reads the [mistakes log](manager-mistakes.md).

## Now

- **Manager: App Manager 10**, created by App Manager 9 at Nathan's direction (OD-58), in `Glow App - No Stream`, on the manager branch `claude/magical-wozniak-yfmmx2` (its outcome branch; PR40 stays), subscribed to PR40.
- **Never ask Nathan to perform a GitHub operation** (OD-58; AM9-10). A CI failure that seems to call for a re-run goes to the Dev Manager first (OD-32), with options that need no action from him.
- **Now: P06.2-F**, the mobile hardening ([brief](../planning/p06-2-f-mobile-hardening.md), revision 5; [record](../testing/evidence/2026-11-01-p06-2-f-mobile-hardening.md)), in PR40. C1 to C3 are verified. **Correction C4** (`691dfba`, branch `claude/upbeat-mccarthy-499h9k`, not integrated) carries DM-40's words; its run failed in two jobs it does not touch: a rendered race (`profile-preferences.spec.ts:321`, 2 of 31 runs) and `setup-python` `504`s, which recurred (PR run 42469365545). **PR40's gate can go red on any head until C5 lands;** a red run is not settled by a re-run (OD-21).
- **[DM-41](../continuity/dev-manager/reviews/2026-11-08-dm-41-p06-2-f-c4-run-failure.md)** (Dev Manager 4, `49ef4a4`, merged at `2c6c1fd`) approved **repair pass C5** in `Glow App - No Stream`: the spec's wait, one toolchain retry in the workflow, C4's code verified by C5's run, and C4's record finished by C5. Its OD-58 texts (6.1 to 6.4) and AM9-12 are applied.
- **C5 is done and integrated** (code head `7f1df96`; runs 42481684565 and 42483045373 green). Its review found two forms inside C4's narrowed callback words; [DM-42](../continuity/dev-manager/reviews/2026-11-08-dm-42-p06-2-f-c5-review-findings.md) (`b338ea2`, merged at `158b16a`) approved comment-only words that state the rule's pairing, and confirmed DM-41's deferred items. **In flight: [C6's prompt](../ephemeral/2026-11-08-p06-2-f-c6-correction-prompt.md)**, revision 1, given to Nathan once Codex has read its commit.
- **The repository is public for now** (OD-51); before it goes private, Nathan tells the manager (`'ccr-**'`, M07).
- **The order** (OD-49): P06.2-F, P06.3, the server slices SV1 to SV4, then P07 to P12; P06.2-T and P07.2a where the Work Register places them, and M07, the costed list (OD-50), before P09 and P11B.
- **Done:** P00 to P05 (fixture scope), M01 to M06, P06.1, P06.DB, P06.2 and P09.3a ([matrix](../planning/store-legal-safety-requirements.md); OD-55).
- **Review log:** DM-01 to DM-41, with "Deferred conditions". **Linear (OD-29).** Every prompt names its environment (OD-36, OD-40, OD-43).

## Waiting checkpoint (8 November 2026, 14:35 UTC, App Manager 10)

| Who waits | On whom | For what | If nothing arrives |
|---|---|---|---|
| App Manager 10 | Codex (an external party), then Nathan running C6 | Codex on the prompt's commit; then C6's report, relayed | Codex: `@codex review` once after 60 minutes (OD-53); C6: nothing to chase (AM6-01) |

## Next actions (App Manager 10)

1. **On C6's report:** verify and integrate it; then its delta review on DM-42 5.1 to 5.3, after Codex on C6's head and the review prompt's commit.
2. **Then** the Dev Manager's next consultation (DM-42's deferred: C6's prompt, the CI line, C6's words), the pre-merge checklist, the merge and its receipt.
3. **Then** P06.3 and the slices, each named to Nathan before it starts (OD-49); the second A05 message before SV2's brief (the carried-items file).

**Carried follow-ups** live in their owning homes: the P06.2 brief's "Carried to later changes", the M02 brief, the P11 plan, [`carried-to-later-items.md`](../planning/carried-to-later-items.md) and the review log's "Deferred conditions".

## Branches and PRs (`git ls-remote`, 8 November 2026, 14:35 UTC)

- **Open: PR40** (P06.2-F), from the manager branch. `main` is at `bac3c19`.
- **Kept, by the cleanup's keep-list:** `main`, the manager branch, and `claude/dev-manager` (`b338ea2`, merged into the manager branch).
- **In PR40's item, all merged into the manager branch:** `claude/practical-wozniak-fg1e2i` (`02f1972`), `claude/trusting-cori-gxlila` (`0e98f25`), `claude/inspiring-ramanujan-tjpril` (`3c0acfe`), `ccr-7506019b-5rfdfn` (`14e37a6`), `claude/upbeat-mccarthy-499h9k` (`691dfba`, C4) and `claude/inspiring-ride-chqpjx` (`e4f9728`, C5); the cleanup deletes each once PR40 merges into `main`.
