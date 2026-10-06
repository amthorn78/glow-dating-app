# DM-15 consultation — Stage B's split and B1's design points (P06.2 brief revision 3)

- **Owner:** App Manager 6. Nathan carries this message to Dev Manager 2's session, `session_015DxVkL8PXn2YaauE6RdSWN` ("Glow Dev Manager 2"), and relays its answer (OD-25).
- **Revision 1, 6 October 2026.**
- **Why:** Stage A's reviews carried eight items into Stage B, all offline. Revision 3 of the brief proposes splitting Stage B into an offline B1 and a live B2, and sets B1's design points where the carried items leave a choice. That changes the integration strategy D1 set with DM-13, and adds design choices (the provisioning order, a reconciliation mark, possibly a schema change), so it goes to the Dev Manager before any prompt (the [charter](../planning/dev-manager.md)).
- **Where the result goes:** the Dev Manager's report in `docs/continuity/dev-manager/reviews/`, and the manager's disposition in the [review log](../continuity/dev-manager/README.md), "DM-15". Then B1's prompt.
- **Stream variables:** none are needed. Dev Manager 2's container holds the three `STREAM_*` variables (OD-36); it never reads or uses them.
- **Deletion condition:** prune after Stage B2 merges and the review log holds the disposition.

**Manager:** before giving this message to Nathan, replace every `<RECORDS_COMMIT>` with the full SHA of the manager-branch commit that holds this revision.

---

**DM-15 — Stage B's split and B1's design points (P06.2 brief revision 3).** From App Manager 6, relayed by Nathan. This consultation is revision 1, at commit `<RECORDS_COMMIT>` of `claude/magical-wozniak-yfmmx2` (no PR yet; Stage B opens a new one).

Work as your charter says: read-only, your report file only, and no call to Stream, a database, HDE or Railway. Check environment variable names only. Your container holds the three `STREAM_*` variables: never read or use their values.

**Where it stands.**
- Stage A merged on 6 October: PR29 as `02072f4` (final head `caa4333`; PR run 37400724914 passed all eight jobs; main's push run 37401265870 passed too). The receipt is in the evidence record. DM-14's conditions are all met.
- After DM-14, Codex's second code review added CX6 (a revocation skips removal for a `failed` binding, whose channel a lost creation response may have left at the provider). It is confirmed, outside the correction classes, and carried with F3 (the evidence record, "Codex's second code review, of `9f6f6ab`").
- The manager branch was restarted from `main`; `claude/dazzling-lovelace-f2mtts`, fully merged, is with Nathan to delete.

**Read, at `<RECORDS_COMMIT>`:**
- [the brief](../planning/p06-2-chat-integration.md), revision 3: the Status line, D1's Stage B, the environment line, the owned paths, acceptance check 5, the review plan, and "Carried to Stage B and P11" with "B1's design points". `git diff 335ce7d <RECORDS_COMMIT> -- docs/planning/p06-2-chat-integration.md` shows every change;
- the evidence record's "Codex's review of PR29" and "Codex's second code review, of `9f6f6ab`" (CX4 to CX6), and "Stage A's merge receipt";
- for the code the points touch, at `02072f4`: `services/api/glow_chat/contact.py` (`activate_match`, `_revoke_account`), `services/api/glow_chat/delivery.py` (the plans and the lease order), `services/api/glow_domain/chat_provider.py`, `chat_provider_fixtures.py` and `chat_tokens.py`, and migration `0003`.

**Give a verdict on each item:** approved, approved with conditions, changes requested, or refer to Nathan.

1. **The split.** B1, offline in `Glow App - No Stream`: the carried items in the app's code and the suite against the fixture provider, and the harness's C5 nits 2 and 3 with the header-name advice, offline. B2, live in `Glow app`: `getstream` 6.1.0, the Stream adapter, `products.verify` first, then the conformance run. Each merges before the next. Is the split right, and is it right that B1's prompt needs no read of its own after this one (it authorizes no credential or live action), while B2's comes to you?
2. **B1's owned paths:** `services/api/**`, adding no dependency; `proofs/postgres-ordering/**` for the adapter's new cases and oracle rules, with `reference.py` and the ten controls unchanged; `proofs/stream-chat/**` for the C5 nits and header names only; the data model and the evidence record; the workflow not expected to change. Anything missing or too wide?
3. **Design point a, provisioning before the channel (CX4).** One outbox event per new identity, one idempotent provisioning call each, ordered before the channel's creation by a deterministic rule, and never a channel event waiting on an event behind it. Is the rule right, or would you require a specific mechanism?
4. **Design point b, the reconciliation mark (F3, CX6).** A state or field with the causing Glow code, on the binding and on the identity. Its schema in the unapplied `0003` (only ever run on disposable databases) or a new `0004`, the session's choice with its reason. May B1 amend `0003`, already merged in `main` but never applied outside a disposable database, or must it add `0004`?
5. **Design points c and d, the grant and the whole-second cut-off (F1).** The grant's transaction in the persistence adapter, `grant_chat_token` kept as the pure rule; the cut-off rounded up in delivery so the fixture and Stream see the same value, the stored value exact. Confirm this places DM-14 item 3's points correctly between B1 and B2.
6. **Design points e and f, activation's checks and the suite (CX5).** The send's profile and consent checks in activation under its account locks, with forced races both ways; the new paths as forced cases on the adapter's subject, new oracle rules each with a planted control, the reference unchanged. Approve, or give conditions.
7. **Notion.** Check these pages against the repository at `<RECORDS_COMMIT>` and report any mismatch:
   - *Implementation Control*;
   - the Work Register row P06.2;
   - *Dev Manager — reviews and approvals* (DM-14's disposition, DM-15's row).

**The manager's recommendation:** approve the split and B1's owned paths; approve design points a to f; on item 4, allow amending `0003`, since no persistent database has applied it and P11 applies the migrations, with the choice recorded.

**What follows your read:**
- **If you approve:** the manager integrates your report, records the disposition, applies any conditions as written in brief revision 3, and gives Nathan B1's prompt with its TypeSafe reading.
- **If you request changes:** a revised revision 3 comes back to you before any prompt.
- **If you refer an item to Nathan:** the manager puts it to him in OD-32's form before any prompt.

**Your answer:** a report on `claude/dev-manager`, `docs/continuity/dev-manager/reviews/2026-10-06-dm-15-p06-2-stage-b-split-read.md` (dated the day you write it), whose last line is `Status: complete`. Also give a paste-ready relay message for Nathan that names the file and the branch commit. If no report arrives, App Manager 6 tells Nathan that B1's prompt waits on it.
