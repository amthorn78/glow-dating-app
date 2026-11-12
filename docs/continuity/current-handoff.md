# Current handoff — App Manager 11 (12 November 2026; SV3 Stage A in PR45; DM-62, then correction C1)

This file only routes: the current item, what happens next and who waits on whom. Each fact lives in one home, listed in the [documentation map](../README.md); earlier handoffs are in `docs/continuity/history/`, the last as [P06.2 to its merge](history/p06-2-handoff.md).

- **Process:** Nathan's manual relay ([manager workflow](../planning/manager-workflow.md)), with the [Dev Manager](../planning/dev-manager.md) as second-layer reviewer (OD-25). Standing directions: the [owner-direction register](owner-directions.md). A new manager starts from the [start procedure](../planning/start-prompts/next-manager.md) and reads the [mistakes log](manager-mistakes.md).

## Now

- **Manager: App Manager 11**, created by App Manager 10 at Nathan's direction ([OD-63](owner-directions.md)), in `Glow App - No Stream`, on the manager branch `claude/magical-wozniak-yfmmx2` (its outcome branch; on the cleanup's keep-list). [PR45](https://github.com/amthorn78/glow-dating-app/pull/45), SV3 Stage A, is open from this branch. App Manager 10 pushed nothing after its handover commit `8130439`.
- **Dev Manager 4** (`session_01Q789u2u6fuC4fQPtHzP9gN`; OD-59) holds `claude/dev-manager`. Nathan carries each consultation to it (OD-25).
- **Never ask Nathan to perform a GitHub operation** (OD-58; AM9-10). A CI failure that seems to call for a re-run goes to the Dev Manager first (OD-32), with options that need no action from him.
- **SV2 is done** (OD-49): [the brief](../planning/sv2-profiles-media.md), revision 8; PR43 at `4dc2061` and PR44 at `3240ef0`, with their receipts in the [evidence record](../testing/evidence/2026-11-10-sv2-profiles-media.md).
- **SV3 is the current item** (OD-49): eligibility, discovery and interactions. [The brief](../planning/sv3-eligibility-discovery-interactions.md), revision 3 (DM-60's Q1 to Q20; DM-61's K1 to K7). Stage A is in PR45 (the [record](../testing/evidence/2026-11-11-sv3-eligibility-discovery-interactions.md)); correction C1 (CX1's lock cycle; V1's tie-break, which Codex's CX2 repeats) comes before its exact-head review. Codex's CX3 (a card's age above 150) is with the Dev Manager as DM-62, and C1's prompt is held for it. Stage B follows after Stage A merges.
- **CI note:** on 11 November, three PR runs failed only at Mobile checks' Chromium install on the runners' package mirror (15:03 to 15:53 UTC). DM-59 section 7 is the rule for a repeat; the step's retry is carried to the next workflow change.
- **The repository is public for now** (OD-51); before it goes private, Nathan tells the manager (`'ccr-**'`, M07).
- **The order** (OD-49): the server slices SV1 to SV4, then P07 to P12; P06.2-T and P07.2a where the Work Register places them, and M07, the costed list (OD-50), before P09 and P11B.
- **Done:** P00 to P05 (fixture scope), M01 to M06, P06.1, P06.DB, P06.2, P09.3a, P06.2-F, P06.3, SV1 and SV2 ([matrix](../planning/store-legal-safety-requirements.md); OD-55).
- **Review log:** DM-01 to DM-62 (DM-62 open), with "Deferred conditions"; DM-62 confirms DM-61's K1 to K7 as applied. **Linear (OD-29).** Every prompt names its environment (OD-36, OD-40, OD-43).

## Waiting checkpoint (12 November 2026, 00:49 UTC, App Manager 11)

| Who waits | On whom | For what | If nothing arrives |
|---|---|---|---|
| App Manager 11 | Codex, then Nathan and Dev Manager 4 | Codex on the commit holding DM-62 (CX3, a card's age above 150), then DM-62's answer; then C1's prompt, revision 3 | No other prompt goes to Nathan (OD-29); a Codex pass with no result after 60 minutes gets one `@codex review` (OD-53) |

## Next actions (App Manager 11)

1. **SV3** (OD-49): DM-62's answer; correction C1 (CX1, V1, CX3) and its verification; PR45's run and Codex on C1's head; the exact-head review of `ad9ff08` and C1 (its prompt's revision 2); the Dev Manager's pre-merge read; the merge. Stage B's prompt only after that.
2. **The decision message on the identity verification company and the photo check's service** (OD-61; DM-52 section 16), after the matrix's recheck of the rows they touch; nothing in SV3 waits on it unless its brief says so.
3. **Then SV4.**

**Carried follow-ups** live in their owning homes: the P06.2 brief's "Carried to later changes", the M02 brief, the P11 plan, [`carried-to-later-items.md`](../planning/carried-to-later-items.md) and the review log's "Deferred conditions".

## Branches and PRs (12 November 2026, 00:33 UTC)

- **Open PRs:** [PR45](https://github.com/amthorn78/glow-dating-app/pull/45), SV3 Stage A, from the manager branch. `main` is at `3240ef0` (PR44).
- **Remote branches:** `main`; the manager branch `claude/magical-wozniak-yfmmx2`; `claude/dev-manager` (`133a715`, DM-61's report, merged at `ee2ebd8`); Stage A's session branch `claude/loving-maxwell-cqu7eq` (`4dee875`, fully merged into the manager branch; the cleanup deletes it once Stage A's PR merges).
