# Current handoff — App Manager 11 (15 November 2026; B0 merged at `947576d`; Stage B next)

This file only routes: the current item, what happens next and who waits on whom. Each fact lives in one home, listed in the [documentation map](../README.md); earlier handoffs are in `docs/continuity/history/`, the last as [P06.2 to its merge](history/p06-2-handoff.md).

- **Process:** Nathan's manual relay ([manager workflow](../planning/manager-workflow.md)), with the [Dev Manager](../planning/dev-manager.md) as second-layer reviewer (OD-25). Standing directions: the [owner-direction register](owner-directions.md). A new manager starts from the [start procedure](../planning/start-prompts/next-manager.md) and reads the [mistakes log](manager-mistakes.md).

## Now

- **Manager: App Manager 11**, created by App Manager 10 at Nathan's direction ([OD-63](owner-directions.md)), in `Glow App - No Stream`, on the manager branch `claude/magical-wozniak-yfmmx2` (its outcome branch; on the cleanup's keep-list). [PR45](https://github.com/amthorn78/glow-dating-app/pull/45), SV3 Stage A, merged at `8d83474`; [PR46](https://github.com/amthorn78/glow-dating-app/pull/46), B0, at `947576d`. App Manager 10 pushed nothing after its handover commit `8130439`.
- **Dev Manager 5** (`session_01Q789u3CWg6s9pBGXerCQZt`; OD-65) holds `claude/dev-manager`. Nathan carries each consultation to it (OD-25).
- **Never ask Nathan to perform a GitHub operation** (OD-58; AM9-10). A CI failure that seems to call for a re-run goes to the Dev Manager first (OD-32), with options that need no action from him.
- **SV2 is done** (OD-49): PR43, PR44 (`3240ef0`), receipts in its [evidence record](../testing/evidence/2026-11-10-sv2-profiles-media.md).
- **SV3 is the current item** (OD-49): eligibility, discovery and interactions. [The brief](../planning/sv3-eligibility-discovery-interactions.md), revision 14 (with DM-60 to DM-72). **Stage A is done:** PR45 merged at `8d83474` with corrections C1 to C5. **B0 is done:** PR46 merged at `947576d` (the [record](../testing/evidence/2026-11-11-sv3-eligibility-discovery-interactions.md), its merge receipts). DM-68 froze the lock scan's rules after C4. **Stage B** (items 4 to 7, D14's record of the row locks the suites send, and its section's four items) is next, from `947576d`; its prompt follows `main`'s push run on it. F7 is decided (OD-64), carried to before P11.
- **CI note:** a Chromium-install failure at Mobile checks follows DM-59 section 7.
- **The repository is public for now** (OD-51); before it goes private, Nathan tells the manager (`'ccr-**'`, M07).
- **The order** (OD-49): the server slices SV1 to SV4, then P07 to P12; P06.2-T and P07.2a where the Work Register places them, and M07, the costed list (OD-50), before P09 and P11B.
- **Done:** P00 to P05 (fixture scope), M01 to M06, P06.1, P06.DB, P06.2, P09.3a, P06.2-F, P06.3, SV1 and SV2 ([matrix](../planning/store-legal-safety-requirements.md); OD-55).
- **Review log:** DM-01 to DM-72, with "Deferred conditions"; DM-72 confirms CC1 to CC4 as applied. **Linear (OD-29).** Every prompt names its environment (OD-36, OD-40, OD-43).

## Waiting checkpoint (15 November 2026, 03:55 UTC, App Manager 11)

| Who waits | On whom | For what | If nothing arrives |
|---|---|---|---|
| App Manager 11 | GitHub | `main`'s push run 43673382167 on `947576d` | Then the receipt's run line and Stage B's prompt, in one commit (AM11-21); a failed run is diagnosed first |

## Next actions (App Manager 11)

1. **SV3** (OD-49): Stage B's verification, its PR, Codex, the exact-head review with its threat model, Dev Manager 5's pre-merge read and its merge.
2. **The decision message on the identity verification company and the photo check's service** (OD-61; DM-52 section 16), after the matrix's recheck of the rows they touch; nothing in SV3 waits on it unless its brief says so.
3. **Then SV4.**

**Carried follow-ups** live in their owning homes: the P06.2 brief's "Carried to later changes", the M02 brief, the P11 plan, [`carried-to-later-items.md`](../planning/carried-to-later-items.md) and the review log's "Deferred conditions".

## Branches and PRs (15 November 2026, 03:55 UTC)

- **Open PRs:** none. `main` is at `947576d` (PR46).
- **Remote branches:** `main`; the manager branch `claude/magical-wozniak-yfmmx2`; `claude/dev-manager` (`04b89d3`, DM-72's report, merged at `05dd38a`). The cleanup run 43673382231 deleted B0's session branch `claude/focused-ride-q5itu1`.
