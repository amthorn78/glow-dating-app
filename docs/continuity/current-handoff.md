# Current handoff — App Manager 12 (19 November 2026; M09 done; DM-94 with Nathan)

This file only routes: the current item, what happens next and who waits on whom. Each fact lives in one home, listed in the [documentation map](../README.md); earlier handoffs are in `docs/continuity/history/`, the last as [P06.2 to its merge](history/p06-2-handoff.md).

- **Process:** Nathan's manual relay ([manager workflow](../planning/manager-workflow.md)), with the [Dev Manager](../planning/dev-manager.md) as second-layer reviewer (OD-25). Standing directions: the [owner-direction register](owner-directions.md). A new manager starts from the [start procedure](../planning/start-prompts/next-manager.md) and reads [GAPP-PF02](../pf-canon/GAPP-PF02-Manager-Practice-Rules.md), the standing practice rules, before the [mistakes log](manager-mistakes.md).

## Now

- **Manager: App Manager 12** ([OD-67](owner-directions.md)), in `Glow App - No Stream`, on the manager branch `claude/magical-wozniak-yfmmx2` (its outcome branch; on the cleanup's keep-list).
- **Dev Manager 5** (`session_01Q789u3CWg6s9pBGXerCQZt`; OD-65) holds `claude/dev-manager`. Nathan carries each consultation to it (OD-25).
- **Never ask Nathan to perform a GitHub operation** (OD-58). A failure that seems to need a re-run goes to the Dev Manager first (OD-32).
- **M09 is done** (OD-72; [its record](../testing/evidence/2026-11-18-m09-project-status-review.md), merged at `c48b950`, with "Manager verification of M09"). Nathan's directions in and after it: **OD-73** (it wrote PF01 1.19, `b738529`, and the plan in Notion, marked pending), **OD-74** (`amthorn78/glow-docs` attached to every session, read-only) and **OD-75** (D-01, D-02, D-03, D-06, D-07 as recommended; D-04 and D-05 wait for P08.3's brief).
- **DM-94** ([the consultation](../ephemeral/2026-11-19-dm-94-m09-plan-and-process.md)) asks the Dev Manager to read PF01 1.19 at `b738529`, the D-06 and D-07 texts (`AGENTS.md`, the manager workflow, the charter, PF02-R19), PF02 1.8 (AM12-22 to AM12-30), `CLAUDE.md` for OD-74 and the CI policy (R-21). None is in force until its read and the pull request carrying it merges; the charter's sentence for OD-76, written after DM-94's commit, needs the next read too; Notion's M09 edits say "pending its merge" until then.
- **SV3, M08, A05-V to A05-V3 and SV2-R are done** (PR45 to PR54). A05 stays open for its third message, before P07.1. The founding-member offer is "lifetime" meaning for as long as Glow runs the service (OD-71).
- **CI note:** a Chromium-install failure is recorded in DM-59, item 7, written for PR44; its retry is routed to SV4 Stage A.
- **The repository is public for now** (OD-51).
- **The order** (PF01 1.19, pending): M07, then A01-R; SV4 (two stages), SV5, SV2-L, AC1 to AC3, then P07 to P12. Under D-06 a Markdown-only item may run beside a code item once DM-94 approves the text.
- **Done:** P00 to P05 (fixture scope), M01 to M06, M08, M09, P06.1, P06.DB, P06.2, P09.3a, P06.2-F, P06.3, SV1 to SV3 and SV2-R.
- **Owner directions:** OD-01 to OD-76 (OD-76: the Dev Manager's read stays; no AWS usage; Maker left open). **Review log:** DM-01 to DM-93. **Linear (OD-29).** Every prompt names its environment (OD-36) and glow-docs as attached (OD-74).

## Waiting checkpoint (19 November 2026, 00:40 UTC, App Manager 12)

| Who waits | On whom | For what | If nothing arrives |
|---|---|---|---|
| App Manager 12 | Nathan, then Dev Manager 5 | DM-94 carried, and the Dev Manager's answer | No governing change merges; M07's brief is written meanwhile |

## Next actions (App Manager 12)

1. **DM-94's answer:** its disposition, a records batch with its conditions, then one pull request of the manager branch into `main` (ordinary documentation), and Notion's "pending" markings removed.
2. **M07,** the costed list: its brief and prompt are written meanwhile and go to Nathan after DM-94's answer. Then **A01-R**; M09-R, the record corrections, beside a code item (D-06).
3. **Manager records after DM-94:** the State of the App (R-07), the review log (R-15), SV2's brief (R-10), Notion (R-26), the pruning (R-28).

**Carried follow-ups** live in their owning homes: [`carried-to-later-items.md`](../planning/carried-to-later-items.md) (with "Routed by M09"), the P11 plan, the review log's "Deferred conditions".

## Branches and PRs (19 November 2026, 00:40 UTC; listed with the GitHub tools before this time)

- **Open PRs:** none. `main` is at `6edae78` (PR54).
- **Remote branches, four:** `main`; the manager branch; `claude/dev-manager` (`adb769d`); M09's `claude/nifty-euler-3v8sl7` (`20a0d99`, merged into the manager branch).
