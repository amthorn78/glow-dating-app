# Current handoff — App Manager 12 (17 November 2026; OD-68's two questions with Nathan; PR50)

This file only routes: the current item, what happens next and who waits on whom. Each fact lives in one home, listed in the [documentation map](../README.md); earlier handoffs are in `docs/continuity/history/`, the last as [P06.2 to its merge](history/p06-2-handoff.md).

- **Process:** Nathan's manual relay ([manager workflow](../planning/manager-workflow.md)), with the [Dev Manager](../planning/dev-manager.md) as second-layer reviewer (OD-25). Standing directions: the [owner-direction register](owner-directions.md). A new manager starts from the [start procedure](../planning/start-prompts/next-manager.md) and reads [GAPP-PF02](../pf-canon/GAPP-PF02-Manager-Practice-Rules.md), the standing practice rules, before the [mistakes log](manager-mistakes.md).

## Now

- **Manager: App Manager 12** ([OD-67](owner-directions.md)), created by App Manager 11 (OD-31), in `Glow App - No Stream`, on the manager branch `claude/magical-wozniak-yfmmx2` (its outcome branch; on the cleanup's keep-list). App Manager 11's handover commit is `69af405`.
- **Dev Manager 5** (`session_01Q789u3CWg6s9pBGXerCQZt`; OD-65) holds `claude/dev-manager`. Nathan carries each consultation to it (OD-25).
- **Never ask Nathan to perform a GitHub operation** (OD-58; AM9-10). A failure that seems to need a re-run goes to the Dev Manager first (OD-32).
- **SV3 is done** (OD-49; PR45 to PR47, `36a19f7`; [the brief](../planning/sv3-eligibility-discovery-interactions.md)). A block's direction is carried to SV4, before P11 (DM-75); F7 to before P11 (OD-64).
- **M08 is done** (OD-66; PR48, `c7716e3`; PF02's revision 1.1 in PR49, `cf0ac60`; its [record](../testing/evidence/2026-11-16-m08-manager-practice-canon.md), sections 12 to 14).
- **A05-V is integrated** (the [brief](../planning/a05-v-verification-services.md), revision 2; its [record](../testing/evidence/2026-11-17-a05-v-verification-services.md), with the manager's verification in section 12; merged at `e038596`). After it, Nathan changed OD-61: **OD-68**, no selfie-to-ID match for the MVP, a card check at signup during a free trial of a paid plan, ID validation kept possible later, and the photo check dropped behind a toggle. **DM-84** (Dev Manager 5) approved its design with QQ1 to QQ23: two questions go to Nathan first (a paid plan at launch, A06; what the card check is for), then A05-V2 if his answers need research; one bounded change to SV2's requirements, full scope, before P10.
- **CI note:** a Chromium-install failure at Mobile checks follows DM-59 section 7.
- **The repository is public for now** (OD-51); before it goes private, Nathan tells the manager (`'ccr-**'`, M07).
- **The order** (OD-49): the server slices SV1 to SV4, then P07 to P12; P06.2-T and P07.2a where the Work Register places them, and M07, the costed list (OD-50), before P09 and P11B.
- **Done:** P00 to P05 (fixture scope), M01 to M06, P06.1, P06.DB, P06.2, P09.3a, P06.2-F, P06.3, SV1, SV2, SV3 and M08.
- **Owner directions:** OD-01 to OD-68. **Review log:** DM-01 to DM-84, with "Deferred conditions". **Linear (OD-29).** Every prompt names its environment (OD-36, OD-40, OD-43).

## Waiting checkpoint (17 November 2026, 18:03 UTC, App Manager 12)

| Who waits | On whom | For what | If nothing arrives |
|---|---|---|---|
| App Manager 12 | Nathan | OD-68's two questions (DM-84 section 4): a paid plan at launch (A06); what the card check is for | No A05-V2 brief and no change to SV2's requirements |
| App Manager 12 | GitHub | PR50's run and Codex on its final head | PR50 stays open |

## Next actions (App Manager 12)

1. **PR50** (A05-V, OD-68, PF02's revision 1.2, DM-83 and DM-84 with their texts): its checklist on DM-84's read, the merge and its receipt; then AM12-15 into PF02-R54 (revision 1.3) for the Dev Manager's next read.
2. **Nathan's answers:** recorded; then A05-V2's brief to the Dev Manager if they need research; the card-check decision message, with the staff question, read by the Dev Manager before Nathan.
3. **Then** the bounded change to SV2's requirements (its brief to the Dev Manager first; before P10), and SV4, each named to Nathan before it starts (OD-29).

**Carried follow-ups** live in their owning homes: the P06.2 brief's "Carried to later changes", the M02 brief, the P11 plan, [`carried-to-later-items.md`](../planning/carried-to-later-items.md) and the review log's "Deferred conditions".

## Branches and PRs (17 November 2026, 15:34 UTC)

- **Open PRs:** none. `main` is at `cf0ac60` (PR49).
- **Remote branches, four:** `main`; the manager branch; `claude/dev-manager` (`3c0a5fe`, merged at `55b8f8a`); A05-V's `claude/vigilant-ramanujan-jbxqro` (`0859532`), merged into the manager branch at `e038596`; the cleanup deletes it when PR50 merges.
