# Current handoff — App Manager 11 (15 November 2026; Stage B's exact-head review with Nathan)

This file only routes: the current item, what happens next and who waits on whom. Each fact lives in one home, listed in the [documentation map](../README.md); earlier handoffs are in `docs/continuity/history/`, the last as [P06.2 to its merge](history/p06-2-handoff.md).

- **Process:** Nathan's manual relay ([manager workflow](../planning/manager-workflow.md)), with the [Dev Manager](../planning/dev-manager.md) as second-layer reviewer (OD-25). Standing directions: the [owner-direction register](owner-directions.md). A new manager starts from the [start procedure](../planning/start-prompts/next-manager.md) and reads the [mistakes log](manager-mistakes.md).

## Now

- **Manager: App Manager 11**, created by App Manager 10 at Nathan's direction ([OD-63](owner-directions.md)), in `Glow App - No Stream`, on the manager branch `claude/magical-wozniak-yfmmx2` (its outcome branch; on the cleanup's keep-list). [PR45](https://github.com/amthorn78/glow-dating-app/pull/45), SV3 Stage A, merged at `8d83474`; [PR46](https://github.com/amthorn78/glow-dating-app/pull/46), B0, at `947576d`. App Manager 10 pushed nothing after its handover commit `8130439`.
- **Dev Manager 5** (`session_01Q789u3CWg6s9pBGXerCQZt`; OD-65) holds `claude/dev-manager`. Nathan carries each consultation to it (OD-25).
- **Never ask Nathan to perform a GitHub operation** (OD-58; AM9-10). A CI failure that seems to call for a re-run goes to the Dev Manager first (OD-32), with options that need no action from him.
- **SV2 is done** (OD-49): PR43, PR44 (`3240ef0`), receipts in its [evidence record](../testing/evidence/2026-11-10-sv2-profiles-media.md).
- **SV3 is the current item** (OD-49): eligibility, discovery and interactions. [The brief](../planning/sv3-eligibility-discovery-interactions.md), revision 16 (with DM-60 to DM-74). **Stage A is done:** PR45 merged at `8d83474` with corrections C1 to C5. **B0 is done:** PR46 merged at `947576d` (the [record](../testing/evidence/2026-11-11-sv3-eligibility-discovery-interactions.md), its merge receipts). DM-68 froze the lock scan's rules after C4. **Stage B** (items 4 to 7, D14's record, its section's six items) stopped at its stop rule (branch `claude/brave-brown-o90q6i`, `29fad40`, app code only; AM11-23, AM11-24); DM-73 ruled on the stop (harness locks `FOR NO KEY UPDATE`, the six earlier tests named, `callproc` planted and the README corrected), and Stage B's prompt, revision 2, continued it on the same branch. **Stage B is built, verified and integrated** (code head `5d58993`; run of record 43686623299, all eight jobs; the record, "Manager verification of Stage B"); PR47 is open. Codex's one finding on it (no read gives a client the directional version) is fixed in Stage B as correction B-C1 (DM-74: one owner-only read). **B-C1 is built, verified and integrated** (code head `470d97a`; run of record 43727020292, all eight jobs). PR47's runs on `6d71ce0` passed all eight jobs and Codex found nothing on that head; the exact-head review prompt (revision 1, for `470d97a`) is with Nathan. F7 is decided (OD-64), carried to before P11.
- **CI note:** a Chromium-install failure at Mobile checks follows DM-59 section 7.
- **The repository is public for now** (OD-51); before it goes private, Nathan tells the manager (`'ccr-**'`, M07).
- **The order** (OD-49): the server slices SV1 to SV4, then P07 to P12; P06.2-T and P07.2a where the Work Register places them, and M07, the costed list (OD-50), before P09 and P11B.
- **Done:** P00 to P05 (fixture scope), M01 to M06, P06.1, P06.DB, P06.2, P09.3a, P06.2-F, P06.3, SV1 and SV2 ([matrix](../planning/store-legal-safety-requirements.md); OD-55).
- **Review log:** DM-01 to DM-74, with "Deferred conditions"; DM-74 confirms EE1 to EE10 as applied; FF1 to FF6 await confirmation at the next consultation. **Linear (OD-29).** Every prompt names its environment (OD-36, OD-40, OD-43).

## Waiting checkpoint (15 November 2026, 15:48 UTC, App Manager 11)

| Who waits | On whom | For what | If nothing arrives |
|---|---|---|---|
| App Manager 11 | Nathan | Stage B's exact-head review report, from its prompt (`docs/ephemeral/2026-11-15-sv3-stage-b-review-prompt.md`, from `6d71ce0`) | No other prompt goes to Nathan (OD-29); no code change on the manager branch until the review's findings are disposed |

## Next actions (App Manager 11)

1. **SV3** (OD-49): the exact-head review's report on `470d97a` (Stage B with B-C1), with its threat model; its findings' dispositions (a correction, or the records), with Dev Manager 5 where a design or a class is in question; Dev Manager 5's pre-merge read (the CI policy's paragraph, the data model's and the contract's rewritten texts, FF1 to FF6 as applied); the merge.
2. **The decision message on the identity verification company and the photo check's service** (OD-61; DM-52 section 16), after the matrix's recheck of the rows they touch; nothing in SV3 waits on it unless its brief says so.
3. **Then SV4.**

**Carried follow-ups** live in their owning homes: the P06.2 brief's "Carried to later changes", the M02 brief, the P11 plan, [`carried-to-later-items.md`](../planning/carried-to-later-items.md) and the review log's "Deferred conditions".

## Branches and PRs (15 November 2026, 15:29 UTC)

- **Open PRs:** [PR47](https://github.com/amthorn78/glow-dating-app/pull/47), SV3 Stage B, from the manager branch. `main` is at `947576d` (PR46).
- **Remote branches:** `main`; the manager branch `claude/magical-wozniak-yfmmx2`; `claude/dev-manager` (`5a74183`, DM-74's report, merged at `e67e1b2`); Stage B's session branch `claude/brave-brown-o90q6i` (`291edef`, integrated into the manager branch by fast-forward). B-C1's session branch `claude/sv3-stage-b-correction-tekmc2` (`53d3988`, integrated into the manager branch by fast-forward). The cleanup run 43673382231 deleted B0's session branch `claude/focused-ride-q5itu1`.
