# Current handoff — App Manager 10 (8 November 2026; P06.2-F, DM-41)

This file only routes: the current item, what happens next and who waits on whom. Each fact lives in one home, listed in the [documentation map](../README.md); earlier handoffs are in `docs/continuity/history/`, the last as [P06.2 to its merge](history/p06-2-handoff.md).

- **Process:** Nathan's manual relay ([manager workflow](../planning/manager-workflow.md)), with the [Dev Manager](../planning/dev-manager.md) as second-layer reviewer (OD-25). Standing directions: the [owner-direction register](owner-directions.md). A new manager starts from the [start procedure](../planning/start-prompts/next-manager.md) and reads the [mistakes log](manager-mistakes.md).

## Now

- **Manager: App Manager 10**, created by App Manager 9 at Nathan's direction (OD-58), in `Glow App - No Stream`, on the manager branch `claude/magical-wozniak-yfmmx2` (its outcome branch; PR40 stays; on the cleanup's keep-list). It subscribes to PR40. App Manager 9 pushes nothing after its handover commit.
- **Never ask Nathan to perform a GitHub operation** (OD-58; AM9-10). A CI failure that seems to call for a re-run goes to the Dev Manager first (OD-32), with options that need no action from him.
- **Now: P06.2-F**, the mobile hardening ([brief](../planning/p06-2-f-mobile-hardening.md), revision 5; [record](../testing/evidence/2026-11-01-p06-2-f-mobile-hardening.md)), in PR40. C1 to C3 are verified. **Correction C4** (`691dfba`, branch `claude/upbeat-mccarthy-499h9k`, not integrated) carries DM-40's words; its run failed in two jobs it does not touch: a rendered race (`profile-preferences.spec.ts:321`, 2 of 31 runs) and `setup-python` `504`s, which recurred (PR run 42469365545). **PR40's gate can go red on any head until C5 lands;** a red run is not settled by a re-run (OD-21).
- **[DM-41](../continuity/dev-manager/reviews/2026-11-08-dm-41-p06-2-f-c4-run-failure.md)** (Dev Manager 4, `49ef4a4`, merged at `2c6c1fd`) approved **repair pass C5** in `Glow App - No Stream`: the spec's wait, one toolchain retry in the workflow, C4's code verified by C5's run, and C4's record finished by C5. Its OD-58 texts (6.1 to 6.4) and AM9-12 are applied.
- **In flight: [C5's prompt](../ephemeral/2026-11-08-p06-2-f-c5-repair-prompt.md)**, revision 1, given to Nathan once Codex has read the commit that holds it (step 6).
- **The repository is public for now** (OD-51); before it goes private, Nathan tells the manager (`'ccr-**'`, M07).
- **The order** (OD-49): P06.2-F, P06.3, the server slices SV1 to SV4, then P07 to P12; P06.2-T and P07.2a where the Work Register places them, and M07, the costed list (OD-50), before P09 and P11B.
- **Done:** P00 to P05 (fixture scope), M01 to M06, P06.1, P06.DB, P06.2 and P09.3a ([matrix](../planning/store-legal-safety-requirements.md); OD-55).
- **Review log:** DM-01 to DM-41, with "Deferred conditions". **Linear (OD-29).** Every prompt names its environment (OD-36, OD-40, OD-43).

## Waiting checkpoint (8 November 2026, 10:51 UTC, App Manager 10)

| Who waits | On whom | For what | If nothing arrives |
|---|---|---|---|
| App Manager 10 | Nathan, running C5 (a session running) | C5's report, relayed | Nothing to chase; its run of record is the session's (AM6-01) |

## Next actions (App Manager 10)

1. **On C5's report:** verify it against its branch and run of record; integrate it; add DM-41 2.4's paragraph to the CI policy; record the outcome in the brief.
2. **Then** C5's review on DM-41 5.1 to 5.3, after Codex on C5's head and the prompt's commit; then the Dev Manager's next consultation (its "Deferred conditions": 1.8, 2.4, 6.2 to 6.4, DM-40 4.2's record part); then the pre-merge checklist, the merge and its receipt.
3. **Then** P06.3 and the slices, each named to Nathan before it starts (OD-49); the second A05 message before SV2's brief (the carried-items file).

**Carried follow-ups** live in their owning homes: the P06.2 brief's "Carried to later changes", the M02 brief, the P11 plan, [`carried-to-later-items.md`](../planning/carried-to-later-items.md) and the review log's "Deferred conditions".

## Branches and PRs (`git ls-remote`, 8 November 2026, 10:51 UTC)

- **Open: PR40** (P06.2-F), from the manager branch. `main` is at `bac3c19`.
- **Kept, by the cleanup's keep-list:** `main`, the manager branch, and `claude/dev-manager` (`49ef4a4`, merged into the manager branch).
- **Unmerged, all in PR40's item:** `claude/practical-wozniak-fg1e2i` (`02f1972`), `claude/trusting-cori-gxlila` (`0e98f25`), `claude/inspiring-ramanujan-tjpril` (`3c0acfe`), `ccr-7506019b-5rfdfn` (`14e37a6`) and `claude/upbeat-mccarthy-499h9k` (`691dfba`, C4, not integrated); the cleanup deletes each once it is fully merged.
