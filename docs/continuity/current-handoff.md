# Current handoff — App Manager 11 (15 November 2026; correction B-C2 with Nathan)

This file only routes: the current item, what happens next and who waits on whom. Each fact lives in one home, listed in the [documentation map](../README.md); earlier handoffs are in `docs/continuity/history/`, the last as [P06.2 to its merge](history/p06-2-handoff.md).

- **Process:** Nathan's manual relay ([manager workflow](../planning/manager-workflow.md)), with the [Dev Manager](../planning/dev-manager.md) as second-layer reviewer (OD-25). Standing directions: the [owner-direction register](owner-directions.md). A new manager starts from the [start procedure](../planning/start-prompts/next-manager.md) and reads the [mistakes log](manager-mistakes.md).

## Now

- **Manager: App Manager 11** ([OD-63](owner-directions.md)), in `Glow App - No Stream`, on the manager branch `claude/magical-wozniak-yfmmx2` (its outcome branch; on the cleanup's keep-list).
- **Dev Manager 5** (`session_01Q789u3CWg6s9pBGXerCQZt`; OD-65) holds `claude/dev-manager`. Nathan carries each consultation to it (OD-25).
- **Never ask Nathan to perform a GitHub operation** (OD-58; AM9-10). A CI failure that seems to call for a re-run goes to the Dev Manager first (OD-32), with options that need no action from him.
- **SV3 is the current item** (OD-49): eligibility, discovery and interactions. [The brief](../planning/sv3-eligibility-discovery-interactions.md), revision 17 (DM-60 to DM-75); its status line and "Sessions" give the history. **Stage A** merged in PR45 (`8d83474`) and **B0** in PR46 (`947576d`). **Stage B with correction B-C1** is built, verified and integrated (code head `470d97a`) and in [PR47](https://github.com/amthorn78/glow-dating-app/pull/47), whose runs and Codex are clean at `e75649d`. **Its exact-head review returned changes required** (no blocking finding; seven should-fix findings in correction classes, nine nits; the [record](../testing/evidence/2026-11-11-sv3-eligibility-discovery-interactions.md), "Exact-head review of Stage B"). DM-75 carried the block's direction to SV4 (sealed until P11), made undo one step and approved correction B-C2 for the rest; B-C2's prompt is with Nathan; Codex's four findings since `c9bca52` are all the review's (#1 carried; #2, #4, #5 in B-C2). F7 is decided (OD-64), carried to before P11.
- **CI note:** a Chromium-install failure at Mobile checks follows DM-59 section 7.
- **The repository is public for now** (OD-51); before it goes private, Nathan tells the manager (`'ccr-**'`, M07).
- **The order** (OD-49): the server slices SV1 to SV4, then P07 to P12; P06.2-T and P07.2a where the Work Register places them, and M07, the costed list (OD-50), before P09 and P11B.
- **Done:** P00 to P05 (fixture scope), M01 to M06, P06.1, P06.DB, P06.2, P09.3a, P06.2-F, P06.3, SV1 and SV2.
- **Review log:** DM-01 to DM-75, with "Deferred conditions" (DM-75's words await confirmation at the pre-merge read). **Linear (OD-29).** Every prompt names its environment (OD-36, OD-40, OD-43).

## Waiting checkpoint (15 November 2026, 23:07 UTC, App Manager 11)

| Who waits | On whom | For what | If nothing arrives |
|---|---|---|---|
| App Manager 11 | Nathan | Correction B-C2's report, from its prompt (`docs/ephemeral/2026-11-15-sv3-stage-b-c2-prompt.md`, from the commit after `c0d3afc`; given after Codex's review of that commit) | No other prompt goes to Nathan (OD-29); nothing written to B-C2's owned paths until its branch is integrated (AM11-21) |

## Next actions (App Manager 11)

1. **SV3** (OD-49): B-C2's report and its verification; PR47's run and Codex; a bounded delta re-review; Dev Manager 5's pre-merge read (the CI policy's paragraph, the data model, the contract texts); the merge.
2. **The decision message on the identity verification company and the photo check's service** (OD-61; DM-52 section 16), after the matrix's recheck of the rows they touch; nothing in SV3 waits on it unless its brief says so.
3. **Then SV4.**

**Carried follow-ups** live in their owning homes: the P06.2 brief's "Carried to later changes", the M02 brief, the P11 plan, [`carried-to-later-items.md`](../planning/carried-to-later-items.md) and the review log's "Deferred conditions".

## Branches and PRs (15 November 2026, 23:07 UTC)

- **Open PRs:** PR47, SV3 Stage B, from the manager branch. `main` is at `947576d` (PR46).
- **Remote branches:** `main`; the manager branch; `claude/dev-manager` (`ab1520b`, DM-75's report, merged at `c0d3afc`); Stage B's session branch `claude/brave-brown-o90q6i` (`291edef`) and B-C1's `claude/sv3-stage-b-correction-tekmc2` (`53d3988`), each integrated by fast-forward.
