# Current handoff — App Manager 12 (17 November 2026; DM-88 with the Dev Manager)

This file only routes: the current item, what happens next and who waits on whom. Each fact lives in one home, listed in the [documentation map](../README.md); earlier handoffs are in `docs/continuity/history/`, the last as [P06.2 to its merge](history/p06-2-handoff.md).

- **Process:** Nathan's manual relay ([manager workflow](../planning/manager-workflow.md)), with the [Dev Manager](../planning/dev-manager.md) as second-layer reviewer (OD-25). Standing directions: the [owner-direction register](owner-directions.md). A new manager starts from the [start procedure](../planning/start-prompts/next-manager.md) and reads [GAPP-PF02](../pf-canon/GAPP-PF02-Manager-Practice-Rules.md), the standing practice rules, before the [mistakes log](manager-mistakes.md).

## Now

- **Manager: App Manager 12** ([OD-67](owner-directions.md)), created by App Manager 11 (OD-31), in `Glow App - No Stream`, on the manager branch `claude/magical-wozniak-yfmmx2` (its outcome branch; on the cleanup's keep-list). App Manager 11's handover commit is `69af405`.
- **Dev Manager 5** (`session_01Q789u3CWg6s9pBGXerCQZt`; OD-65) holds `claude/dev-manager`. Nathan carries each consultation to it (OD-25).
- **Never ask Nathan to perform a GitHub operation** (OD-58; AM9-10). A failure that seems to need a re-run goes to the Dev Manager first (OD-32).
- **SV3 is done** (OD-49; PR45 to PR47, `36a19f7`; [the brief](../planning/sv3-eligibility-discovery-interactions.md)). A block's direction is carried to SV4, before P11 (DM-75); F7 to before P11 (OD-64).
- **M08 is done** (OD-66; PR48, `c7716e3`; PF02's revision 1.1 in PR49, `cf0ac60`; its [record](../testing/evidence/2026-11-16-m08-manager-practice-canon.md), sections 12 to 14).
- **A05-V is done** (PR50, `0a0c4fd`; its [record](../testing/evidence/2026-11-17-a05-v-verification-services.md)). **OD-68** then set ID verification aside for the MVP (a card check at signup; the photo check behind a toggle); **DM-84** sent two questions to Nathan, and **OD-69** answered: a paid plan and no free plan; a free trial at signup with a card; free accounts only by staff grant; the stores' billing with a Stripe link; the card check for all three purposes. A05-V2's [brief](../planning/a05-v2-card-check-and-paid-trial.md), revision 2, was approved in **DM-85**, with PF01's revision 1.18; both are in `main` with PR51 (`a316a3a`); A05-V2's research, OD-70 and PF02 1.4 and 1.5 with PR52 (`d57da65`). **A05-V2** is done (its [record](../testing/evidence/2026-11-17-a05-v2-card-check-and-paid-trial.md)): Stripe reviews a dating service, and does not exclude it. **DM-86** approved the card-check decision message with SS1 to SS14; Nathan accepted it (**OD-70**) and added a founding-member offer (up to 1,000 members, $100 for life, ideally Stripe only); **DM-87** sent the offer to research: A05-V3's [brief](../planning/a05-v3-founding-member-offer.md), revision 1, is with the Dev Manager (DM-88). One bounded change to SV2's requirements follows, before P10 (DM-84).
- **CI note:** a Chromium-install failure at Mobile checks follows DM-59 section 7.
- **The repository is public for now** (OD-51); before it goes private, Nathan tells the manager (`'ccr-**'`, M07).
- **The order** (OD-49): the server slices SV1 to SV4, then P07 to P12; P06.2-T and P07.2a where the Work Register places them, and M07, the costed list (OD-50), before P09 and P11B.
- **Done:** P00 to P05 (fixture scope), M01 to M06, P06.1, P06.DB, P06.2, P09.3a, P06.2-F, P06.3, SV1, SV2, SV3 and M08.
- **Owner directions:** OD-01 to OD-70. **Review log:** DM-01 to DM-88, with "Deferred conditions". **Linear (OD-29).** Every prompt names its environment (OD-36, OD-40, OD-43).

## Waiting checkpoint (17 November 2026, 23:12 UTC, App Manager 12)

| Who waits | On whom | For what | If nothing arrives |
|---|---|---|---|
| App Manager 12 | Nathan, carrying DM-88 to Dev Manager 5 | DM-88's report ([consultation](../ephemeral/2026-11-17-dm-88-a05-v3-brief-and-pf02-1-6.md)): A05-V3's brief, DM-87's texts, PF02 1.6 | No prompt is written; no pull request opens |

## Next actions (App Manager 12)

1. **DM-88:** its disposition; then A05-V3's prompt, scored, to Nathan; the session; the verification.
2. **The offer's decision message**, to the Dev Manager before Nathan.
3. **Then** the bounded change to SV2's requirements (its brief to the Dev Manager; full scope; before P10), and SV4, each named to Nathan before it starts (OD-29).

**Carried follow-ups** live in their owning homes: the P06.2 brief's "Carried to later changes", the M02 brief, the P11 plan, [`carried-to-later-items.md`](../planning/carried-to-later-items.md) and the review log's "Deferred conditions".

## Branches and PRs (17 November 2026, 23:10 UTC)

- **Open PRs:** none. `main` is at `d57da65` (PR52).
- **Remote branches, three:** `main`; the manager branch; `claude/dev-manager` (`b8e289c`, merged at `1213569`). The cleanup deleted A05-V2's branch at PR52's merge.
