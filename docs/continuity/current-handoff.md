# Current handoff — App Manager 6 (23 October 2026, P06.2)

This file only routes: the current item, what happens next and who waits on whom. Each fact lives in one home, listed in the [documentation map](../README.md); earlier handoffs are in `docs/continuity/history/`, the last as [P06.DB to its merge](history/p06-db-handoff.md).

- **Process:** Nathan's manual relay ([manager workflow](../planning/manager-workflow.md)), with the [Dev Manager](../planning/dev-manager.md) as second-layer reviewer (OD-25). Standing directions: the [owner-direction register](owner-directions.md). A new manager starts from the [start procedure](../planning/start-prompts/next-manager.md) and reads the [mistakes log](manager-mistakes.md).

## Now

- **Manager:** App Manager 6, `session_01MxuepyycrEWf5uFjpwEird`, created by App Manager 5 (`session_01Xv2QTYGpc5bSQQoVeWiN4E`) on 5 October at Nathan's direction (OD-38, OD-31), in `Glow App - No Stream`. It holds the manager branch `claude/magical-wozniak-yfmmx2`, restarted from `main` at `3272eed` after PR30 merged; B2's work goes in a new PR. App Manager 5 pushes nothing after `a1eb9dc`.
- **Current item: P06.2**, the chat integration (PF01 P06), resumed on 5 October (OD-38). Its [brief](../planning/p06-2-chat-integration.md), revision 5, splits Stage B into B1 (offline) and B2 (live). **Stage A merged** (PR29, `02072f4`) and **Stage B1 merged** (PR30, `3272eed`, 22 October). **Stage B2's offline work is integrated (`957dccb`), and its live run stopped at `baseline`** on Stream's additions since 27 September, so **P06.2 is stopped** (the brief's design point a; ADR 0003's condition (c)). The disposition and the correction pass B2-C1 are with the Dev Manager in DM-17. P06.2 is done only when Stage C merges.
  - **Carried to P06.2:** P06.DB's six items are done in Stage A; the [P06.1 brief](../planning/p06-1-chat-provider-proof.md)'s four remain for Stage B and later.
- **Next item: M04**, "Branch hygiene: automatic cleanup of merged branches" (OD-39), after P06.2 merges (OD-29).
- **Done:** P06.1 (`47db18d`), P06.DB (`3afffb3`); P06.2 Stages A (`02072f4`) and B1 (`3272eed`).
- **[HDE contract request](../planning/hde-contract-request.md)** (OD-23): in Nathan's own process; on delivery, record the receipt (its section 6).
- **Dev Manager 2:** `session_015DxVkL8PXn2YaauE6RdSWN` (OD-35); [review log](dev-manager/README.md), DM-01 to DM-17.

## Waiting checkpoint (23 October 2026)

| Who waits | On whom | For what | If nothing arrives |
|---|---|---|---|
| App Manager 6 | Nathan | DM-17's report (the [consultation](../ephemeral/2026-10-23-dm-17-p06-2-stage-b2-drift-read.md)), carried to Dev Manager 2; his pick for B2 (the session's commits name Fable 5.1; the rung is not recorded); the deletion of `claude/gracious-newton-4fjsmn` and `claude/kind-ride-brzl8u` | Tell Nathan P06.2 waits on it; nothing else starts (OD-29) |

## Next actions (App Manager 6)

1. **DM-17:** integrate the report, record the dispositions, apply its conditions as written in the brief and in B2-C1's [prompt](../ephemeral/2026-10-23-p06-2-stage-b2-c1-correction-prompt.md) revision 2, score it again and give it to Nathan for `Glow app`. An item DM-17 refers to Nathan goes to him in OD-32's form first; the D8 question (the brief's point vi), if referred, goes to him after B2-C1's live rows and before Stage C.
2. **After B2-C1:** verify and integrate it. A code that differs from the fixture's for F3 and CX6's causes blocks the merge until it is dispositioned. Then one exact-head review of B2 and B2-C1 together, whose prompt names its security focus areas (DM-16 1.5) and the manager's five points in "Manager verification of Stage B2"; Codex's code review on the final head (OD-41); B2's PR and its merge. Then Stage C.
3. **M04, after P06.2 merges:** brief, then the Dev Manager's read, then the implementation prompt for `Glow App - No Stream`. Starting points: push to `main` and manual dispatch only, never a pull-request event; `contents: write` for that job only, no secrets, pinned actions; delete only a branch whose head is in `main`, off a keep-list held on `main` (`main`, the manager branch, and `claude/dev-manager` by name, DM-13 item 10) and heading no open PR; dry-run mode and a job summary; selection tests and a run of record; the CI policy updated, classified with the pre-change policy, the whole workflow diff read; exact-head review, Codex and the Dev Manager's read.
3a. **OD-43** (23 October): the manager workflow's step 3 and the environment inventory name Nathan's CLI agent in an open environment. The step 3 sentence is governing Markdown after DM-17's commit (`5ae3c23`), so the next consultation asks the Dev Manager to read it before B2's PR merges.
4. **Standing:** before the next Dev Manager session, rewrite its start prompt (DM-03 E3; DM-07 item 7), which still names `claude/stoic-carson-66gdig`.

**Recorded follow-ups:** uv 0.12.17 in `scripts/bootstrap-toolchain.sh` (the API README's lock command names it; B2 used a scratch install); the harness client lock's high-severity `npm` advisory (B2-C1 names it); a newer upload-artifact pin (DM-09 item 1); at the next change to each file, `CLAUDE.md`'s environment phrase, the environment inventory's No Stream Setup script, and a pointer to OD-35 in PF01's D10 (DM-09 item 2 (b)); prune the P06.1 and P06.DB prompts in `docs/ephemeral/` once their links are commit-pinned; Setup-script and pin-test hardening (M02 brief); a stale-documentation sweep of `docs/architecture/`, `docs/testing/` and `docs/operations/`.

## Branches (checked on GitHub at PR30's merge, 22 October 2026)

- **5 remote branches:** `main` (`3272eed`); `claude/magical-wozniak-yfmmx2` (kept); `claude/dev-manager` (kept by name); `claude/gracious-newton-4fjsmn` and `claude/kind-ride-brzl8u` (fully merged: **to delete**).
- **Earlier deletions** (5 October): see OD-39 in the owner-direction register and AM5-24 in the mistakes log.
