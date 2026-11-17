# Current handoff — App Manager 12 (17 November 2026; the card-check decision with Nathan)

This file only routes: the current item, what happens next and who waits on whom. Each fact lives in one home, listed in the [documentation map](../README.md); earlier handoffs are in `docs/continuity/history/`, the last as [P06.2 to its merge](history/p06-2-handoff.md).

- **Process:** Nathan's manual relay ([manager workflow](../planning/manager-workflow.md)), with the [Dev Manager](../planning/dev-manager.md) as second-layer reviewer (OD-25). Standing directions: the [owner-direction register](owner-directions.md). A new manager starts from the [start procedure](../planning/start-prompts/next-manager.md) and reads [GAPP-PF02](../pf-canon/GAPP-PF02-Manager-Practice-Rules.md), the standing practice rules, before the [mistakes log](manager-mistakes.md).

## Now

- **Manager: App Manager 12** ([OD-67](owner-directions.md)), created by App Manager 11 (OD-31), in `Glow App - No Stream`, on the manager branch `claude/magical-wozniak-yfmmx2` (its outcome branch; on the cleanup's keep-list). App Manager 11's handover commit is `69af405`.
- **Dev Manager 5** (`session_01Q789u3CWg6s9pBGXerCQZt`; OD-65) holds `claude/dev-manager`. Nathan carries each consultation to it (OD-25).
- **Never ask Nathan to perform a GitHub operation** (OD-58; AM9-10). A failure that seems to need a re-run goes to the Dev Manager first (OD-32).
- **SV3 is done** (OD-49; PR45 to PR47, `36a19f7`; [the brief](../planning/sv3-eligibility-discovery-interactions.md)). A block's direction is carried to SV4, before P11 (DM-75); F7 to before P11 (OD-64).
- **M08 is done** (OD-66; PR48, `c7716e3`; PF02's revision 1.1 in PR49, `cf0ac60`; its [record](../testing/evidence/2026-11-16-m08-manager-practice-canon.md), sections 12 to 14).
- **A05-V is done** (PR50, `0a0c4fd`; its [record](../testing/evidence/2026-11-17-a05-v-verification-services.md)). **OD-68** then set ID verification aside for the MVP (a card check at signup; the photo check behind a toggle); **DM-84** sent two questions to Nathan, and **OD-69** answered: a paid plan and no free plan; a free trial at signup with a card; free accounts only by staff grant; the stores' billing with a Stripe link; the card check for all three purposes. A05-V2's [brief](../planning/a05-v2-card-check-and-paid-trial.md), revision 2, was approved in **DM-85**, with PF01's revision 1.18; both are in `main` with PR51 (`a316a3a`). **A05-V2's session** is verified and merged into the manager branch (`d046b0f`; its [record](../testing/evidence/2026-11-17-a05-v2-card-check-and-paid-trial.md), section 14): Stripe reviews a dating service before accepting it, and does not exclude it. **DM-86** approved the card-check decision message with SS1 to SS14 (revision 2), and it is with Nathan. One bounded change to SV2's requirements follows, before P10 (DM-84).
- **CI note:** a Chromium-install failure at Mobile checks follows DM-59 section 7.
- **The repository is public for now** (OD-51); before it goes private, Nathan tells the manager (`'ccr-**'`, M07).
- **The order** (OD-49): the server slices SV1 to SV4, then P07 to P12; P06.2-T and P07.2a where the Work Register places them, and M07, the costed list (OD-50), before P09 and P11B.
- **Done:** P00 to P05 (fixture scope), M01 to M06, P06.1, P06.DB, P06.2, P09.3a, P06.2-F, P06.3, SV1, SV2, SV3 and M08.
- **Owner directions:** OD-01 to OD-69. **Review log:** DM-01 to DM-86, with "Deferred conditions". **Linear (OD-29).** Every prompt names its environment (OD-36, OD-40, OD-43).

## Waiting checkpoint (17 November 2026, 22:32 UTC, App Manager 12)

| Who waits | On whom | For what | If nothing arrives |
|---|---|---|---|
| App Manager 12 | Nathan | His answers to the [decision message](../ephemeral/2026-11-17-a05-card-check-decision-message.md), C1 to C5 | No OD row; PR52 is not opened |

## Next actions (App Manager 12)

1. **Nathan's answers:** a new OD row; the carried-items file's P07 and P08.3 entries; the Work Register's A05 and A06 rows. Then PR52 (A05-V2, PF02 1.4 and 1.5, DM-86, the message and the answer's records), after the Dev Manager reads the OD row, PF02 1.5 and the message as sent, Codex and the checklist.
2. **Then** the bounded change to SV2's requirements (its brief to the Dev Manager; full scope; before P10), and SV4, each named to Nathan before it starts (OD-29).

**Carried follow-ups** live in their owning homes: the P06.2 brief's "Carried to later changes", the M02 brief, the P11 plan, [`carried-to-later-items.md`](../planning/carried-to-later-items.md) and the review log's "Deferred conditions".

## Branches and PRs (17 November 2026, 22:32 UTC)

- **Open PRs:** none. `main` is at `a316a3a` (PR51).
- **Remote branches, four:** `main`; the manager branch; `claude/dev-manager` (`5a53db6`, merged at `a429ccd`); A05-V2's `claude/a05-v2-glow-card-check-1ucpsx` (`e23829b`, merged at `d046b0f`).
