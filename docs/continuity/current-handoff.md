# Current handoff — App Manager 4 (27 September 2026)

This file only routes: the current item, what happens next and who waits on whom. Each fact lives in one home, listed in the [documentation map](../README.md). The earlier, longer handoff is [archived](history/m02-p06-1-handoff.md) (DM-01 P3).

- **Process:** Nathan's manual relay, per the [manager workflow](../planning/manager-workflow.md), with the [Dev Manager](../planning/dev-manager.md) as the second-layer reviewer; Nathan carries their messages by hand (OD-25).
- **Standing directions:** the [owner-direction register](owner-directions.md). Notion carries a copy of it and of the operating procedure; the repository wins on any difference (OD-26, OD-27).
- **A new manager** starts from the [next-manager start procedure](../planning/start-prompts/next-manager.md) and reads the [mistakes log](manager-mistakes.md).

## Now

- **Manager:** App Manager 4, `session_016nNFAZqaqTDqxX4Bq6jbRV` (Fable 5.1, extra high), created by App Manager 3 on 27 September (OD-31). It pushes `claude/stoic-carson-66gdig`, the head of draft [PR26](https://github.com/amthorn78/glow-dating-app/pull/26). App Manager 3 (`session_01Bx3BmFASvyWm2dsUj5CHhG`) pushes nothing after `642d1f8`. App Manager 4's container holds the three `STREAM_*` variables and never reads or uses them (AM3-17).
- **Current item: P06.1**, the chat-provider permissions and economics proof (resumed 25 September; other feature work paused): the [brief](../planning/p06-1-chat-provider-proof.md) and the [evidence record](../testing/evidence/2026-09-25-p06-1-chat-provider-proof.md).
  - **S15:** confirmed live; the display rule ([ADR 0003](../adr/0003-chat-display-rule.md)) stands, and Nathan's principle is in force (OD-14, OD-16).
  - **Linear (OD-29):** one session at a time, one prompt per message.
    - **Done:** I1 (`9ff600f`) and its review (changes required); the flake fix (`8b8b1bd`), C1 (`e85bba0`), C2 (`63e922f`), C3 (`8c1a8c0`) and I2a (`6a51dae`), each approved by its review; DM-04. No Stream mechanism meets the history policy on its own (I2a).
    - **Done:** DM-05: approved with conditions, all accepted; revision 2 of I2b's [prompt](../ephemeral/2026-09-27-p06-1-i2b-implementation-prompt.md) applies them as written and needs no further read (DM-03 G2). Disposition: the [review log](dev-manager/README.md), "DM-05".
    - **Next:** I2b, live, from revision 2; Nathan adds the `STREAM_*` variables (OD-28) and runs it.
- **The [HDE contract request](../planning/hde-contract-request.md)** (OD-23): Nathan sets the date in HDE's process; on delivery, record the receipt (its section 6).
- **Dev Manager 1:** session `session_01MrcrmqtuENZ345mKfmsSWv`, branch `claude/dev-manager`. Its [review log](dev-manager/README.md) holds DM-01 to DM-05, Nathan's answers and the dispositions.

## Waiting checkpoint (27 September 2026)

| Who waits | On whom | For what | If nothing arrives |
|---|---|---|---|
| App Manager 4 | Nathan | I2b's report, from revision 2 of its prompt | Nothing else starts (OD-29); ask Nathan for the session's state |
| App Manager 4 | Nathan | Confirmation of the shared-restore risk ADR 0004 records as accepted | ADR 0004 stands |
| App Manager 4 | The Dev Manager, via Nathan | Reads of the governing changes after `fa4dc5f` (OD-31's too) and of the HDE contract request, each as its own later step | PR26 cannot merge without the reads |

## Next actions

1. Verify I2b's report against its pushed branch, integrate it and read CI, the new job included; update the CI policy's job names and counts (DM-05 finding 4 (c)). Then I2b's exact-head review prompt, which names the workflow diff and asks the reviewer to confirm from the PR run that the new job ran. After the review, update ADR 0003's conditions (DM-05 finding 5 (b)).
2. Then the economics discovery (the brief's "Sessions"). Live prompts tell Nathan to add the `STREAM_*` variables first (OD-28).
3. Close P06.1:
   - the Dev Manager's reads of the governing Markdown changed after `fa4dc5f`;
   - complete the pre-merge checklist in PR26 (workflow step 7);
   - mark the PR ready and wait for Codex;
   - merge and verify `main`;
   - record the receipt, this handoff and Notion;
   - rotate the development Stream secret (DM-02 B8).
4. **Next item after P06.1:** P06.DB, the early disposable-PostgreSQL proof (OD-17, PF01 §6). Then P06.2.

**Recorded follow-ups** (after P06.1 is clear): the Setup-script and pin-test hardening ([M02 brief](../planning/claude-setup-optimization.md), last sections); a stale-documentation sweep of `docs/architecture/`, `docs/testing/` and `docs/operations/`; failure capture in CI (the flake diagnosis's proposal).

## Branches

- **PR26** is not behind `main`. Its code: I1's harness (`9ff600f`), the flake fix (`8b8b1bd`), C1 (`e85bba0`), C2 (`63e922f`), C3 (`8c1a8c0`) and I2a (`6a51dae`); the rest is Markdown.
- Merged into PR26 only: the session branches the brief names (I1, the flake fix, C1, C2, C3 and I2a) and `claude/dev-manager` (the Dev Manager's reports).
- Retire the unmerged `app-builder-1/p05-1-birth-diagnostics` after PR26 merges.
- Every other remote branch is merged into `main`.
