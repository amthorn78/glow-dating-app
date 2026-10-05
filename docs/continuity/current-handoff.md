# Current handoff — App Manager 5 (5 October 2026, after PR28)

This file only routes: the current item, what happens next and who waits on whom. Each fact lives in one home, listed in the [documentation map](../README.md); the earlier handoff is [archived](history/m02-p06-1-handoff.md).

- **Process:** Nathan's manual relay, per the [manager workflow](../planning/manager-workflow.md), with the [Dev Manager](../planning/dev-manager.md) as second-layer reviewer (OD-25).
- **Standing directions:** the [owner-direction register](owner-directions.md); Notion carries a copy, and the repository wins (OD-26, OD-27).
- **A new manager** starts from the [start procedure](../planning/start-prompts/next-manager.md) and reads the [mistakes log](manager-mistakes.md).

## Now

- **Manager:** App Manager 5 (`session_01Xv2QTYGpc5bSQQoVeWiN4E`), started by Nathan by hand on 27 September. Its branch `claude/magical-wozniak-yfmmx2` fast-forwarded to `main` at `3afffb3` after PR28 merged; the post-merge records ride with the next PR.
- **P06.1 is done** (merged 29 September at `47db18d`): the [brief](../planning/p06-1-chat-provider-proof.md) and the [evidence record](../testing/evidence/2026-09-25-p06-1-chat-provider-proof.md), with its merge receipt. The display rule ([ADR 0003](../adr/0003-chat-display-rule.md)) stands; the development application stays locked down (OD-37).
- **P06.DB is done** (merged 5 October at `3afffb3`): the [brief](../planning/p06-db-disposable-postgres-proof.md), revision 7, whose "Sessions" lists every session, and the [evidence record](../testing/evidence/2026-09-29-p06-db-disposable-postgres-proof.md), with its merge receipt. The proof and the Foundation job "Database proof checks" order sends against every revocation of contact on a disposable PostgreSQL in CI, and the P11 plan marks DB06 and DB09 partially evidenced in CI. **Carried to P06.2** (the brief): six items; items 1 and 6, the reused-database guard and the refusal of `dbshell`, come before P06.2's first run of the suite on any database (DM-09, DM-12).
- **Next item: P06.2**, the chat integration (PF01 P06: the app's chat adapter and server-mediated send authorization, carrying P06.DB's reference design into the app's persistence adapter, and the mobile chat interface). It **waits on Nathan's direction**: OD-12 keeps other feature work paused until he resumes it.
  - **Linear (OD-29):** one session at a time, one prompt per message.
- **The [HDE contract request](../planning/hde-contract-request.md)** (OD-23): in Nathan's own process; on delivery, record the receipt (its section 6); not a standing item for him (OD-32).
- **Dev Manager 2:** session `session_015DxVkL8PXn2YaauE6RdSWN`, created by Dev Manager 1 (OD-35); branch `claude/dev-manager`; the [review log](dev-manager/README.md) holds DM-01 to DM-12, each with its disposition.
- **Environments** (OD-36): every prompt names one; `Glow app` only for a session that calls Stream.

## Waiting checkpoint (5 October 2026, App Manager 5)

| Who waits | On whom | For what | If nothing arrives |
|---|---|---|---|
| App Manager 5 | Nathan | His direction on P06.2 (OD-12) | Nothing to chase: no work item starts without it (OD-08, OD-29) |

## Next actions

1. When Nathan directs P06.2: write its brief from PF01's P06 and both briefs' "Carried to P06.2", and send it to the Dev Manager before any prompt (new components and integration strategy, per the charter). Then the implementation prompt, with its TypeSafe reading and its environment (`Glow app` if the session calls Stream).
2. Standing: before the Stream harness is used live again, the C5 review's nits 2 and 3 and its header-allowlist advice; before the next Dev Manager session, rewrite its start prompt (DM-03 E3; DM-07 item 7).

**Recorded follow-ups:** the manager workflow's rule "Nothing unexplained goes to Nathan" gained a sentence on 5 October (AM5-23): governing Markdown, which the Dev Manager reads before the next PR merges; a newer `actions/upload-artifact` pin (DM-09 item 1); at the next change to each file, `CLAUDE.md`'s environment phrase, the environment inventory's No Stream Setup script once confirmed, and a pointer to OD-35 in PF01's D10 (DM-09 item 2 (b)); prune the P06.1 and P06.DB prompts in `docs/ephemeral/` once their links are commit-pinned; Setup-script and pin-test hardening ([M02 brief](../planning/claude-setup-optimization.md)); a stale-documentation sweep of `docs/architecture/`, `docs/testing/` and `docs/operations/`.

## Branches

- **PR27** merged at `47db18d`: P06.1's code (I1, the flake fix, C1 to C5, I2a, I2b) and its records.
- **PR28** merged at `3afffb3` on 5 October: P06.DB's code and records. No PR is open; the post-merge records are on `claude/magical-wozniak-yfmmx2` for the next PR.
- `claude/dev-manager` merges into the manager branch at each consultation's integration.
- `claude/magical-goldberg-ie0j16` (the second run of C1's prompt, never integrated) can be retired.
- Retire the unmerged `app-builder-1/p05-1-birth-diagnostics` once its content is confirmed recorded; every other remote branch is merged into `main`.
