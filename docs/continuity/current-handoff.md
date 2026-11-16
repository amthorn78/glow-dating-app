# Current handoff — App Manager 11 (16 November 2026; DM-78, then correction B-C4)

This file only routes: the current item, what happens next and who waits on whom. Each fact lives in one home, listed in the [documentation map](../README.md); earlier handoffs are in `docs/continuity/history/`, the last as [P06.2 to its merge](history/p06-2-handoff.md).

- **Process:** Nathan's manual relay ([manager workflow](../planning/manager-workflow.md)), with the [Dev Manager](../planning/dev-manager.md) as second-layer reviewer (OD-25). Standing directions: the [owner-direction register](owner-directions.md). A new manager starts from the [start procedure](../planning/start-prompts/next-manager.md) and reads the [mistakes log](manager-mistakes.md).

## Now

- **Manager: App Manager 11** ([OD-63](owner-directions.md)), in `Glow App - No Stream`, on the manager branch `claude/magical-wozniak-yfmmx2` (its outcome branch; on the cleanup's keep-list).
- **Dev Manager 5** (`session_01Q789u3CWg6s9pBGXerCQZt`; OD-65) holds `claude/dev-manager`. Nathan carries each consultation to it (OD-25).
- **Never ask Nathan to perform a GitHub operation** (OD-58; AM9-10). A failure that seems to need a re-run goes to the Dev Manager first (OD-32).
- **SV3 is the current item** (OD-49). [The brief](../planning/sv3-eligibility-discovery-interactions.md), revision 18 (DM-60 to DM-77); its status line and "Sessions" give the history. **Stage A** merged in PR45 (`8d83474`), **B0** in PR46 (`947576d`). **Stage B with B-C1, B-C2 and B-C3** is in [PR47](https://github.com/amthorn78/glow-dating-app/pull/47) (code head `edc883e`; the [record](../testing/evidence/2026-11-11-sv3-eligibility-discovery-interactions.md)). DM-75 carried the block's direction to SV4 (sealed until P11). B-C2's delta re-review asked for changes, narrowly (no blocking finding); DM-77 ruled on each; correction B-C3 (code head `edc883e`) is built, verified and integrated; its delta re-review asked for changes (no blocking finding), and DM-78 asks Dev Manager 5 for the dispositions before correction B-C4. F7 is decided (OD-64), carried to before P11.
- **CI note:** a Chromium-install failure at Mobile checks follows DM-59 section 7.
- **The repository is public for now** (OD-51); before it goes private, Nathan tells the manager (`'ccr-**'`, M07).
- **The order** (OD-49): the server slices SV1 to SV4, then P07 to P12; P06.2-T and P07.2a where the Work Register places them, and M07, the costed list (OD-50), before P09 and P11B.
- **Done:** P00 to P05 (fixture scope), M01 to M06, P06.1, P06.DB, P06.2, P09.3a, P06.2-F, P06.3, SV1 and SV2.
- **Owner directions:** OD-01 to OD-66. **Review log:** DM-01 to DM-78, with "Deferred conditions" (DM-75's, DM-76's and DM-77's words await confirmation at the pre-merge reads). **Linear (OD-29).** Every prompt names its environment (OD-36, OD-40, OD-43).

## Waiting checkpoint (16 November 2026, 14:40 UTC, App Manager 11)

| Who waits | On whom | For what | If nothing arrives |
|---|---|---|---|
| App Manager 11 | Nathan, Dev Manager 5 | DM-78's answer (B-C3's delta re-review dispositions; D14's freeze); then B-C4's prompt | No other prompt goes to Nathan (OD-29); no code change on the manager branch until B-C4 |

## Next actions (App Manager 11)

1. **SV3** (OD-49): DM-78's answer; the brief's revision 19; B-C4's prompt after Codex's pass; B-C4 and its bounded delta re-review; Dev Manager 5's pre-merge read of PR47; the merge.
2. **M08** (OD-66): PF02 built (`claude/beautiful-pascal-7n0o9n`, `9a90bd8`); DM-76 approved it with HH1 to HH20, applied at integration after PR47.
3. **The decision message on the identity verification company and the photo check's service** (OD-61; DM-52 section 16), after the matrix's recheck of the rows they touch; nothing in SV3 waits on it unless its brief says so.
4. **Then SV4.**

**Carried follow-ups** live in their owning homes: the P06.2 brief's "Carried to later changes", the M02 brief, the P11 plan, [`carried-to-later-items.md`](../planning/carried-to-later-items.md) and the review log's "Deferred conditions".

## Branches and PRs (16 November 2026, 14:40 UTC)

- **Open PRs:** PR47, SV3 Stage B, from the manager branch. `main` is at `947576d` (PR46).
- **Remote branches:** `main`; the manager branch; `claude/dev-manager` (`6bf10c5`, DM-77's report, merged at `76ccea2`); Stage B's session branch `claude/brave-brown-o90q6i` (`291edef`) and B-C1's `claude/sv3-stage-b-correction-tekmc2` (`53d3988`), each integrated by fast-forward; B-C2's `claude/sleepy-newton-1g92x8` (`423f34a`), merged at `4616214`; B-C3's `claude/zealous-dirac-6f5mq2` (`a31a79f`), integrated by fast-forward; M08's `claude/beautiful-pascal-7n0o9n` (`9a90bd8`), held until PR47 merges.
