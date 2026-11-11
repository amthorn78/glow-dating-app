# Current handoff — App Manager 11 (11 November 2026; SV3's brief with the Dev Manager)

This file only routes: the current item, what happens next and who waits on whom. Each fact lives in one home, listed in the [documentation map](../README.md); earlier handoffs are in `docs/continuity/history/`, the last as [P06.2 to its merge](history/p06-2-handoff.md).

- **Process:** Nathan's manual relay ([manager workflow](../planning/manager-workflow.md)), with the [Dev Manager](../planning/dev-manager.md) as second-layer reviewer (OD-25). Standing directions: the [owner-direction register](owner-directions.md). A new manager starts from the [start procedure](../planning/start-prompts/next-manager.md) and reads the [mistakes log](manager-mistakes.md).

## Now

- **Manager: App Manager 11**, created by App Manager 10 at Nathan's direction ([OD-63](owner-directions.md)), in `Glow App - No Stream`, on the manager branch `claude/magical-wozniak-yfmmx2` (its outcome branch; on the cleanup's keep-list). No PR is open: App Manager 11 opens SV3 Stage A's PR from this branch once Stage A has a code head. App Manager 10 pushed nothing after its handover commit `8130439`.
- **Dev Manager 4** (`session_01Q789u2u6fuC4fQPtHzP9gN`; OD-59) holds `claude/dev-manager`. Nathan carries each consultation to it (OD-25).
- **Never ask Nathan to perform a GitHub operation** (OD-58; AM9-10). A CI failure that seems to call for a re-run goes to the Dev Manager first (OD-32), with options that need no action from him.
- **SV2 is done** (OD-49), profiles and media: [the brief](../planning/sv2-profiles-media.md), revision 8 (DM-52 to DM-59; [OD-61](owner-directions.md), [OD-62](owner-directions.md)). Stage A merged with [PR43](https://github.com/amthorn78/glow-dating-app/pull/43) at `4dc2061` (10 November 2026), Stage B with [PR44](https://github.com/amthorn78/glow-dating-app/pull/44) at `3240ef0` (11 November 2026); both merge receipts are in the [evidence record](../testing/evidence/2026-11-10-sv2-profiles-media.md).
- **SV3 is the current item** (OD-49): eligibility, discovery and interactions. [The brief](../planning/sv3-eligibility-discovery-interactions.md), revision 1, rests on the [matrix recheck](../testing/evidence/2026-11-11-sv3-matrix-recheck.md) of 11 November. [DM-60](../ephemeral/2026-11-11-dm-60-sv3-brief.md) is with Nathan to carry to Dev Manager 4; it also confirms DM-59's L1 to L7.
- **CI note:** on 11 November, three PR runs failed only at Mobile checks' Chromium install on the runners' package mirror (15:03 to 15:53 UTC). DM-59 section 7 is the rule for a repeat; the step's retry is carried to the next workflow change.
- **The repository is public for now** (OD-51); before it goes private, Nathan tells the manager (`'ccr-**'`, M07).
- **The order** (OD-49): the server slices SV1 to SV4, then P07 to P12; P06.2-T and P07.2a where the Work Register places them, and M07, the costed list (OD-50), before P09 and P11B.
- **Done:** P00 to P05 (fixture scope), M01 to M06, P06.1, P06.DB, P06.2, P09.3a, P06.2-F, P06.3, SV1 and SV2 ([matrix](../planning/store-legal-safety-requirements.md); OD-55).
- **Review log:** DM-01 to DM-59, with "Deferred conditions"; the next consultation confirms DM-59's L1 to L7 as applied. **Linear (OD-29).** Every prompt names its environment (OD-36, OD-40, OD-43).

## Waiting checkpoint (11 November 2026, 18:13 UTC, App Manager 11)

| Who waits | On whom | For what | If nothing arrives |
|---|---|---|---|
| App Manager 11 | Nathan, then Dev Manager 4 | DM-60's report (a relay, then the Dev Manager's read), given to Nathan at this commit | No SV3 prompt goes to Nathan; App Manager 11 asks him whether Dev Manager 4's session is still available |

## Next actions (App Manager 11)

1. **SV3** (OD-49): receive DM-60's report, record the dispositions, apply its conditions as the brief's revision 2, then Stage A's implementation prompt (D1), with its TypeSafe reading.
2. **The decision message on the identity verification company and the photo check's service** (OD-61; DM-52 section 16), after the matrix's recheck of the rows they touch; nothing in SV3 waits on it unless its brief says so.
3. **Then SV4.**

**Carried follow-ups** live in their owning homes: the P06.2 brief's "Carried to later changes", the M02 brief, the P11 plan, [`carried-to-later-items.md`](../planning/carried-to-later-items.md) and the review log's "Deferred conditions".

## Branches and PRs (`git ls-remote`, 11 November 2026, 17:09 UTC)

- **Open PRs:** none. `main` is at `3240ef0` (PR44).
- **Remote branches:** `main`; the manager branch `claude/magical-wozniak-yfmmx2` (`a9a4e05` when listed; fast-forwarded to `3240ef0`, then this handover commit); `claude/dev-manager` (`d2b46ad`, DM-59's report, merged at `75cf4fc`). All three are on the cleanup's keep-list; the cleanup run 43065281784 deleted Stage B's three session branches.
