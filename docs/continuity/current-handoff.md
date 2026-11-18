# Current handoff — App Manager 12 (18 November 2026; OD-71 and PR53)

This file only routes: the current item, what happens next and who waits on whom. Each fact lives in one home, listed in the [documentation map](../README.md); earlier handoffs are in `docs/continuity/history/`, the last as [P06.2 to its merge](history/p06-2-handoff.md).

- **Process:** Nathan's manual relay ([manager workflow](../planning/manager-workflow.md)), with the [Dev Manager](../planning/dev-manager.md) as second-layer reviewer (OD-25). Standing directions: the [owner-direction register](owner-directions.md). A new manager starts from the [start procedure](../planning/start-prompts/next-manager.md) and reads [GAPP-PF02](../pf-canon/GAPP-PF02-Manager-Practice-Rules.md), the standing practice rules, before the [mistakes log](manager-mistakes.md).

## Now

- **Manager: App Manager 12** ([OD-67](owner-directions.md)), created by App Manager 11 (OD-31), in `Glow App - No Stream`, on the manager branch `claude/magical-wozniak-yfmmx2` (its outcome branch; on the cleanup's keep-list). App Manager 11's handover commit is `69af405`.
- **Dev Manager 5** (`session_01Q789u3CWg6s9pBGXerCQZt`; OD-65) holds `claude/dev-manager`. Nathan carries each consultation to it (OD-25).
- **Never ask Nathan to perform a GitHub operation** (OD-58; AM9-10). A failure that seems to need a re-run goes to the Dev Manager first (OD-32).
- **SV3 is done** (OD-49; PR45 to PR47, `36a19f7`; [the brief](../planning/sv3-eligibility-discovery-interactions.md)). A block's direction is carried to SV4, before P11 (DM-75); F7 to before P11 (OD-64).
- **M08 is done** (OD-66; PR48, `c7716e3`; PF02's revision 1.1 in PR49, `cf0ac60`; its [record](../testing/evidence/2026-11-16-m08-manager-practice-canon.md), sections 12 to 14).
- **A05:** A05-V is done (PR50, `0a0c4fd`). **OD-68** set ID verification aside for the MVP; **OD-69** chose a paid plan with a free trial, staff grants and a Stripe link, and PF01 1.18 records it (PR51). A05-V2 is done (PR52, `d57da65`; its [record](../testing/evidence/2026-11-17-a05-v2-card-check-and-paid-trial.md)), and Nathan accepted its decision message (**OD-70**), adding a founding-member offer (up to 1,000 members, $100 for life, ideally Stripe only). A05-V3, the offer's research ([brief](../planning/a05-v3-founding-member-offer.md), revision 2, DM-88), is verified and merged (`d897720`; its [record](../testing/evidence/2026-11-18-a05-v3-founding-member-offer.md), section 17); **DM-89** approved the offer's decision message with VV1 to VV12, and Nathan answered it, all as recommended (**OD-71**), and DM-90 approved its row with WW1. One bounded change to SV2's requirements follows, before P10 (DM-84).
- **CI note:** a Chromium-install failure at Mobile checks follows DM-59 section 7.
- **The repository is public for now** (OD-51); before it goes private, Nathan tells the manager (`'ccr-**'`, M07).
- **The order** (OD-49): the server slices SV1 to SV4, then P07 to P12; P06.2-T and P07.2a where the Work Register places them, and M07, the costed list (OD-50), before P09 and P11B.
- **Done:** P00 to P05 (fixture scope), M01 to M06, P06.1, P06.DB, P06.2, P09.3a, P06.2-F, P06.3, SV1, SV2, SV3 and M08.
- **Owner directions:** OD-01 to OD-71. **Review log:** DM-01 to DM-90, with "Deferred conditions". **Linear (OD-29).** Every prompt names its environment (OD-36, OD-40, OD-43).

## Waiting checkpoint (18 November 2026, 08:30 UTC, App Manager 12)

| Who waits | On whom | For what | If nothing arrives |
|---|---|---|---|
| App Manager 12 | GitHub | PR53's run and Codex's summary on its final head (DM-90's report, WW1 and AM12-21) | PR53 is not merged |

## Next actions (App Manager 12)

1. **PR53** (A05-V3, PF02 1.6 unchanged, DM-88 to DM-90, the message and OD-71): DM-90's read is done; merged after the run and Codex on the final head and the checklist.
2. **After the merge:** the receipt; the spent files pruned, OD-71's link pinned (DM-90); AM12-20 and AM12-21 into PF02 (1.7).
3. **Then** the bounded change to SV2's requirements (its brief to the Dev Manager; full scope; before P10), and SV4, each named to Nathan before it starts (OD-29).

**Carried follow-ups** live in their owning homes: the P06.2 brief's "Carried to later changes", the M02 brief, the P11 plan, [`carried-to-later-items.md`](../planning/carried-to-later-items.md) and the review log's "Deferred conditions".

## Branches and PRs (18 November 2026, 08:30 UTC)

- **Open PRs:** PR53, from the manager branch. `main` is at `d57da65` (PR52).
- **Remote branches, four:** `main`; the manager branch; `claude/dev-manager` (`1ce329d`, merged at `918442c`); A05-V3's `claude/zealous-ride-v8tszx` (`362edb0`, merged at `d897720`).
