# Current handoff — App Manager 12 (18 November 2026; SV2-R done; M09, the project status review)

This file only routes: the current item, what happens next and who waits on whom. Each fact lives in one home, listed in the [documentation map](../README.md); earlier handoffs are in `docs/continuity/history/`, the last as [P06.2 to its merge](history/p06-2-handoff.md).

- **Process:** Nathan's manual relay ([manager workflow](../planning/manager-workflow.md)), with the [Dev Manager](../planning/dev-manager.md) as second-layer reviewer (OD-25). Standing directions: the [owner-direction register](owner-directions.md). A new manager starts from the [start procedure](../planning/start-prompts/next-manager.md) and reads [GAPP-PF02](../pf-canon/GAPP-PF02-Manager-Practice-Rules.md), the standing practice rules, before the [mistakes log](manager-mistakes.md).

## Now

- **Manager: App Manager 12** ([OD-67](owner-directions.md)), created by App Manager 11 (OD-31), in `Glow App - No Stream`, on the manager branch `claude/magical-wozniak-yfmmx2` (its outcome branch; on the cleanup's keep-list). App Manager 11's handover commit is `69af405`.
- **Dev Manager 5** (`session_01Q789u3CWg6s9pBGXerCQZt`; OD-65) holds `claude/dev-manager`. Nathan carries each consultation to it (OD-25).
- **Never ask Nathan to perform a GitHub operation** (OD-58; AM9-10). A failure that seems to need a re-run goes to the Dev Manager first (OD-32).
- **SV3 is done** (OD-49; PR45 to PR47, `36a19f7`; [the brief](../planning/sv3-eligibility-discovery-interactions.md)). A block's direction is carried to SV4, before P11 (DM-75); F7 to before P11 (OD-64).
- **M08 is done** (OD-66; PR48, `c7716e3`; PF02's revision 1.1 in PR49, `cf0ac60`; its [record](../testing/evidence/2026-11-16-m08-manager-practice-canon.md), sections 12 to 14).
- **A05:** A05-V is done (PR50, `0a0c4fd`). **OD-68** set ID verification aside for the MVP; **OD-69** chose a paid plan with a free trial, staff grants and a Stripe link, and PF01 1.18 records it (PR51). A05-V2 is done (PR52, `d57da65`; its [record](../testing/evidence/2026-11-17-a05-v2-card-check-and-paid-trial.md)), and Nathan accepted its decision message (**OD-70**), adding a founding-member offer (up to 1,000 members, $100 for life, ideally Stripe only). A05-V3, the offer's research, is done (PR53, `15d54f6`; its [record](../testing/evidence/2026-11-18-a05-v3-founding-member-offer.md), sections 17 and 18), and Nathan answered the offer's decision message, all as recommended (**OD-71**). A05 stays open for its third message, before P07's brief.
- **SV2-R is done** (OD-68; PR54, `6edae78`; its [brief](../planning/sv2-r-od-68-requirements-change.md) and [record](../testing/evidence/2026-11-18-sv2-r-requirements-change.md)), with PF02 1.7 (DM-91). Its review asked for tests only, which correction C1 added (AM12-25, AM12-26).
- **M09, the independent project status review,** is the current item (OD-72): one review session reports the build's status and the remaining work to launch ([its brief](../planning/m09-project-status-review.md)). PF02 1.8 and SV4's brief are tabled until it reports.
- **CI note:** a Chromium-install failure at Mobile checks follows DM-59 section 7.
- **The repository is public for now** (OD-51); before it goes private, Nathan tells the manager (`'ccr-**'`, M07).
- **The order** (OD-49): the server slices SV1 to SV4, then P07 to P12; P06.2-T and P07.2a where the Work Register places them, and M07, the costed list (OD-50), before P09 and P11B.
- **Done:** P00 to P05 (fixture scope), M01 to M06, P06.1, P06.DB, P06.2, P09.3a, P06.2-F, P06.3, SV1, SV2, SV3, M08 and SV2-R.
- **Owner directions:** OD-01 to OD-72. **Review log:** DM-01 to DM-93, with "Deferred conditions". **Linear (OD-29).** Every prompt names its environment (OD-36, OD-40, OD-43).

## Waiting checkpoint (18 November 2026, 23:06 UTC, App Manager 12)

| Who waits | On whom | For what | If nothing arrives |
|---|---|---|---|
| App Manager 12 | Nathan | M09's review session and its report ([the prompt](../ephemeral/2026-11-18-m09-project-status-review-prompt.md)) | No verification; nothing else starts (OD-29) |

## Next actions (App Manager 12)

1. **M09's report:** verify its claims, integrate its record with a disposition for each finding, send governing proposals to the Dev Manager and Nathan's decisions to him (OD-32), and refresh the State of the App.
2. **Tabled (OD-72):** PF02 1.8 (AM12-22 to AM12-28 into R14, R01, R17 and R30) and SV4's brief, until Nathan lifts this or M09 routes them.

**Carried follow-ups** live in their owning homes: the P06.2 brief's "Carried to later changes", the M02 brief, the P11 plan, [`carried-to-later-items.md`](../planning/carried-to-later-items.md) and the review log's "Deferred conditions".

## Branches and PRs (18 November 2026, 23:06 UTC)

- **Open PRs:** none. `main` is at `6edae78` (PR54).
- **Remote branches, three:** `main`; the manager branch; `claude/dev-manager` (`adb769d`, merged at `d8e76e2`). The cleanup deleted SV2-R's two session branches after PR54's merge.
