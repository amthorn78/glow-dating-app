# Current handoff — App Manager 12 (17 November 2026; B-C6's report, then PR47's pre-merge read)

This file only routes: the current item, what happens next and who waits on whom. Each fact lives in one home, listed in the [documentation map](../README.md); earlier handoffs are in `docs/continuity/history/`, the last as [P06.2 to its merge](history/p06-2-handoff.md).

- **Process:** Nathan's manual relay ([manager workflow](../planning/manager-workflow.md)), with the [Dev Manager](../planning/dev-manager.md) as second-layer reviewer (OD-25). Standing directions: the [owner-direction register](owner-directions.md). A new manager starts from the [start procedure](../planning/start-prompts/next-manager.md) and reads the [mistakes log](manager-mistakes.md).

## Now

- **Manager: App Manager 12** ([OD-67](owner-directions.md)), created by App Manager 11 (OD-31), in `Glow App - No Stream`, on the manager branch `claude/magical-wozniak-yfmmx2` (its outcome branch; on the cleanup's keep-list). App Manager 11's handover commit is the head when App Manager 12 starts.
- **Dev Manager 5** (`session_01Q789u3CWg6s9pBGXerCQZt`; OD-65) holds `claude/dev-manager`. Nathan carries each consultation to it (OD-25).
- **Never ask Nathan to perform a GitHub operation** (OD-58; AM9-10). A failure that seems to need a re-run goes to the Dev Manager first (OD-32).
- **SV3 is the current item** (OD-49). [The brief](../planning/sv3-eligibility-discovery-interactions.md), revision 21 (DM-60 to DM-80); its status line and "Sessions" give the history. **Stage A** merged in PR45 (`8d83474`), **B0** in PR46 (`947576d`). **Stage B with B-C1 to B-C5** is in [PR47](https://github.com/amthorn78/glow-dating-app/pull/47) (code head `0d784d4`; the [record](../testing/evidence/2026-11-11-sv3-eligibility-discovery-interactions.md)). DM-75 carried the block's direction to SV4 (sealed until P11). D14's rules are frozen from `07d8de3` (DM-78). B-C5's short review asked for one class 5 correction (R1); DM-80 put the limit in one home and ruled a records correction, B-C6. **B-C6 has run** (`claude/intelligent-ride-t4vdpj`: code `bf33fd0`, records `a965f3a`; both push runs passed); its report has not been relayed. F7 is decided (OD-64), carried to before P11.
- **CI note:** a Chromium-install failure at Mobile checks follows DM-59 section 7.
- **The repository is public for now** (OD-51); before it goes private, Nathan tells the manager (`'ccr-**'`, M07).
- **The order** (OD-49): the server slices SV1 to SV4, then P07 to P12; P06.2-T and P07.2a where the Work Register places them, and M07, the costed list (OD-50), before P09 and P11B.
- **Done:** P00 to P05 (fixture scope), M01 to M06, P06.1, P06.DB, P06.2, P09.3a, P06.2-F, P06.3, SV1 and SV2.
- **Owner directions:** OD-01 to OD-67. **Review log:** DM-01 to DM-80, with "Deferred conditions" (DM-75's to DM-80's words await confirmation at the pre-merge reads). **Linear (OD-29).** Every prompt names its environment (OD-36, OD-40, OD-43).

## Waiting checkpoint (17 November 2026, 01:11 UTC, App Manager 11 for App Manager 12)

| Who waits | On whom | For what | If nothing arrives |
|---|---|---|---|
| App Manager 12 | Nathan | B-C6's report, relayed | No other prompt goes to Nathan (OD-29); nothing written to B-C6's owned paths until it is integrated, by merge (it starts at `6970721`, before the handover commit) |

## Next actions (App Manager 12)

1. **SV3** (OD-49): B-C6's report verified and B-C6 integrated; its short review (the brief's "B-C6's review"); Dev Manager 5's pre-merge read of PR47; the merge.
2. **M08** (OD-66): PF02 built (`claude/beautiful-pascal-7n0o9n`, `9a90bd8`); DM-76 approved it with HH1 to HH20, applied at integration after PR47.
3. **The decision message on the identity verification company and the photo check's service** (OD-61; DM-52 section 16), after the matrix's recheck of the rows they touch; nothing in SV3 waits on it unless its brief says so.
4. **Then SV4.**

**Carried follow-ups** live in their owning homes: the P06.2 brief's "Carried to later changes", the M02 brief, the P11 plan, [`carried-to-later-items.md`](../planning/carried-to-later-items.md) and the review log's "Deferred conditions".

## Branches and PRs (17 November 2026, 01:11 UTC)

- **Open PRs:** PR47 alone, SV3 Stage B, from the manager branch. `main` is at `947576d` (PR46).
- **Remote branches, eleven:** `main`; the manager branch; `claude/dev-manager` (`6e67c21`, merged at `9cfe9ce`). Already in the manager branch, deleted by the branch cleanup when PR47 merges: Stage B's `claude/brave-brown-o90q6i`, B-C1's `claude/sv3-stage-b-correction-tekmc2`, B-C2's `claude/sleepy-newton-1g92x8`, B-C3's `claude/zealous-dirac-6f5mq2`, B-C4's `claude/ecstatic-feynman-61wkt0`, B-C5's `claude/brave-gates-1ty8o2`. Not yet in it: B-C6's `claude/intelligent-ride-t4vdpj` (`a965f3a`), awaiting verification; M08's `claude/beautiful-pascal-7n0o9n` (`9a90bd8`), held until PR47 merges. A session cannot delete a branch.
