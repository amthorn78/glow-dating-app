# Current handoff — App Manager 12 (18 November 2026; SV2-R reviewed; correction C1)

This file only routes: the current item, what happens next and who waits on whom. Each fact lives in one home, listed in the [documentation map](../README.md); earlier handoffs are in `docs/continuity/history/`, the last as [P06.2 to its merge](history/p06-2-handoff.md).

- **Process:** Nathan's manual relay ([manager workflow](../planning/manager-workflow.md)), with the [Dev Manager](../planning/dev-manager.md) as second-layer reviewer (OD-25). Standing directions: the [owner-direction register](owner-directions.md). A new manager starts from the [start procedure](../planning/start-prompts/next-manager.md) and reads [GAPP-PF02](../pf-canon/GAPP-PF02-Manager-Practice-Rules.md), the standing practice rules, before the [mistakes log](manager-mistakes.md).

## Now

- **Manager: App Manager 12** ([OD-67](owner-directions.md)), created by App Manager 11 (OD-31), in `Glow App - No Stream`, on the manager branch `claude/magical-wozniak-yfmmx2` (its outcome branch; on the cleanup's keep-list). App Manager 11's handover commit is `69af405`.
- **Dev Manager 5** (`session_01Q789u3CWg6s9pBGXerCQZt`; OD-65) holds `claude/dev-manager`. Nathan carries each consultation to it (OD-25).
- **Never ask Nathan to perform a GitHub operation** (OD-58; AM9-10). A failure that seems to need a re-run goes to the Dev Manager first (OD-32).
- **SV3 is done** (OD-49; PR45 to PR47, `36a19f7`; [the brief](../planning/sv3-eligibility-discovery-interactions.md)). A block's direction is carried to SV4, before P11 (DM-75); F7 to before P11 (OD-64).
- **M08 is done** (OD-66; PR48, `c7716e3`; PF02's revision 1.1 in PR49, `cf0ac60`; its [record](../testing/evidence/2026-11-16-m08-manager-practice-canon.md), sections 12 to 14).
- **A05:** A05-V is done (PR50, `0a0c4fd`). **OD-68** set ID verification aside for the MVP; **OD-69** chose a paid plan with a free trial, staff grants and a Stripe link, and PF01 1.18 records it (PR51). A05-V2 is done (PR52, `d57da65`; its [record](../testing/evidence/2026-11-17-a05-v2-card-check-and-paid-trial.md)), and Nathan accepted its decision message (**OD-70**), adding a founding-member offer (up to 1,000 members, $100 for life, ideally Stripe only). A05-V3, the offer's research, is done (PR53, `15d54f6`; its [record](../testing/evidence/2026-11-18-a05-v3-founding-member-offer.md), sections 17 and 18), and Nathan answered the offer's decision message, all as recommended (**OD-71**). A05 stays open for its third message, before P07's brief.
- **SV2-R,** the bounded change to SV2's requirements after OD-68 (DM-84 section 5; full scope; before P10): its [brief](../planning/sv2-r-od-68-requirements-change.md) and PF02 1.7 were approved in DM-91 to DM-93 (AM12-22, AM12-24). Built on the prompt's revision 2 (code `f4703a1`) and merged into the manager branch; PR54 (with PF02 1.7) is green, and Codex found nothing. The exact-head review found the code right and two guards untested: correction C1 (the brief's revision 7) adds tests only and takes up three carried entries (AM12-26); P11 gets the recheck's notes (AM12-25). Next: C1, a delta review, the merge.
- **CI note:** a Chromium-install failure at Mobile checks follows DM-59 section 7.
- **The repository is public for now** (OD-51); before it goes private, Nathan tells the manager (`'ccr-**'`, M07).
- **The order** (OD-49): the server slices SV1 to SV4, then P07 to P12; P06.2-T and P07.2a where the Work Register places them, and M07, the costed list (OD-50), before P09 and P11B.
- **Done:** P00 to P05 (fixture scope), M01 to M06, P06.1, P06.DB, P06.2, P09.3a, P06.2-F, P06.3, SV1, SV2, SV3 and M08.
- **Owner directions:** OD-01 to OD-71. **Review log:** DM-01 to DM-93, with "Deferred conditions". **Linear (OD-29).** Every prompt names its environment (OD-36, OD-40, OD-43).

## Waiting checkpoint (18 November 2026, 20:44 UTC, App Manager 12)

| Who waits | On whom | For what | If nothing arrives |
|---|---|---|---|
| App Manager 12 | GitHub, then Nathan | Codex's pass on C1's prompt commit (PF02-R39, R42); then C1's session report | No prompt is given; no verification |

## Next actions (App Manager 12)

1. **SV2-R's correction C1:** its [prompt](../ephemeral/2026-11-18-sv2-r-correction-c1-prompt.md) to Nathan once Codex has passed its commit; then the verification and a delta review.
2. **The merge,** which carries PF02 1.7 as DM-91 approved it; then AM12-22 into PF02 (1.8), for the Dev Manager's read.
3. **Then** SV4, named to Nathan before it starts (OD-29).

**Carried follow-ups** live in their owning homes: the P06.2 brief's "Carried to later changes", the M02 brief, the P11 plan, [`carried-to-later-items.md`](../planning/carried-to-later-items.md) and the review log's "Deferred conditions".

## Branches and PRs (18 November 2026, 20:44 UTC)

- **Open PRs:** PR54 (SV2-R). `main` is at `15d54f6` (PR53).
- **Remote branches, four:** `main`; the manager branch; `claude/dev-manager` (`adb769d`, merged at `d8e76e2`); SV2-R's session branch (`587f4a2`, merged at `d996ef6`).
