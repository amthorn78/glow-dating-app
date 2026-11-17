# Current handoff — App Manager 12 (17 November 2026; A05-V integrated; OD-68 at DM-84)

This file only routes: the current item, what happens next and who waits on whom. Each fact lives in one home, listed in the [documentation map](../README.md); earlier handoffs are in `docs/continuity/history/`, the last as [P06.2 to its merge](history/p06-2-handoff.md).

- **Process:** Nathan's manual relay ([manager workflow](../planning/manager-workflow.md)), with the [Dev Manager](../planning/dev-manager.md) as second-layer reviewer (OD-25). Standing directions: the [owner-direction register](owner-directions.md). A new manager starts from the [start procedure](../planning/start-prompts/next-manager.md) and reads [GAPP-PF02](../pf-canon/GAPP-PF02-Manager-Practice-Rules.md), the standing practice rules, before the [mistakes log](manager-mistakes.md).

## Now

- **Manager: App Manager 12** ([OD-67](owner-directions.md)), created by App Manager 11 (OD-31), in `Glow App - No Stream`, on the manager branch `claude/magical-wozniak-yfmmx2` (its outcome branch; on the cleanup's keep-list). App Manager 11's handover commit is `69af405`.
- **Dev Manager 5** (`session_01Q789u3CWg6s9pBGXerCQZt`; OD-65) holds `claude/dev-manager`. Nathan carries each consultation to it (OD-25).
- **Never ask Nathan to perform a GitHub operation** (OD-58; AM9-10). A failure that seems to need a re-run goes to the Dev Manager first (OD-32).
- **SV3 is done** (OD-49): Stage A in PR45 (`8d83474`), B0 in PR46 (`947576d`), Stage B with B-C1 to B-C6 in PR47 (`36a19f7`, 17 November; [the brief](../planning/sv3-eligibility-discovery-interactions.md), revision 21; the [record](../testing/evidence/2026-11-11-sv3-eligibility-discovery-interactions.md)'s merge receipts). A block's direction is carried to SV4, before P11 (DM-75); F7 to before P11 (OD-64).
- **M08 is done** (OD-66): GAPP-PF02, the manager practice canon, merged in PR48 (`c7716e3`, 17 November; its [record](../testing/evidence/2026-11-16-m08-manager-practice-canon.md), sections 12 and 13). PF02's revision 1.1 (AM12-10 to AM12-12), approved as written in DM-83, merged in PR49 (`cf0ac60`; the record, section 14).
- **A05-V is integrated** (the [brief](../planning/a05-v-verification-services.md), revision 2; its [record](../testing/evidence/2026-11-17-a05-v-verification-services.md), with the manager's verification in section 12; merged at `e038596`). After it, Nathan changed OD-61: **OD-68**, no selfie-to-ID match for the MVP, a card check at signup during a free trial of a paid plan, ID validation kept possible later, and the photo check dropped behind a toggle. Its design is at **DM-84**.
- **CI note:** a Chromium-install failure at Mobile checks follows DM-59 section 7.
- **The repository is public for now** (OD-51); before it goes private, Nathan tells the manager (`'ccr-**'`, M07).
- **The order** (OD-49): the server slices SV1 to SV4, then P07 to P12; P06.2-T and P07.2a where the Work Register places them, and M07, the costed list (OD-50), before P09 and P11B.
- **Done:** P00 to P05 (fixture scope), M01 to M06, P06.1, P06.DB, P06.2, P09.3a, P06.2-F, P06.3, SV1, SV2, SV3 and M08.
- **Owner directions:** OD-01 to OD-68. **Review log:** DM-01 to DM-84, with "Deferred conditions". **Linear (OD-29).** Every prompt names its environment (OD-36, OD-40, OD-43).

## Waiting checkpoint (17 November 2026, 15:46 UTC, App Manager 12)

| Who waits | On whom | For what | If nothing arrives |
|---|---|---|---|
| App Manager 12 | Dev Manager 5, through Nathan | DM-84: OD-68's design (the card check with a store-billed trial; the photo check's toggle; SV2's requirements), A05-V's records corrections, PF02's revision 1.2 | Nothing about OD-68 is designed or put to Nathan; no pull request is opened |

## Next actions (App Manager 12)

1. **DM-84's answer:** its records batch; then **PR50** (A05-V's research and verification, OD-68, PF02's revision 1.2), merged after its read, Codex and its checklist.
2. **OD-68** (no selfie-to-ID match for the MVP; a card check at signup during a free trial of a paid plan; the photo check behind a toggle): as DM-84 rules; recommended, a research item A05-V2 on the card check, then a decision message, read by the Dev Manager before Nathan.
3. **Then** the bounded change to SV2's requirements, and SV4, each named to Nathan before it starts (OD-29).

**Carried follow-ups** live in their owning homes: the P06.2 brief's "Carried to later changes", the M02 brief, the P11 plan, [`carried-to-later-items.md`](../planning/carried-to-later-items.md) and the review log's "Deferred conditions".

## Branches and PRs (17 November 2026, 15:34 UTC)

- **Open PRs:** none. `main` is at `cf0ac60` (PR49).
- **Remote branches, four:** `main`; the manager branch; `claude/dev-manager` (`3c0a5fe`, merged at `55b8f8a`); A05-V's `claude/vigilant-ramanujan-jbxqro` (`0859532`), merged into the manager branch at `e038596`; the cleanup deletes it when PR50 merges.
