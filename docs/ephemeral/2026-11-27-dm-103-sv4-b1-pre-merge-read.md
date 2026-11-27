# DM-103 consultation — SV4 B1's pre-merge read (PR60), with B1-C1 and its exact-head review

- **Owner:** App Manager 13. Nathan carries this message to Dev Manager 7's session, `session_01Q789u3mBCcA1Fu21CMJKbS` ("Glow Dev Manager 7") (OD-25, OD-84). App Manager 13 receives the answer.
- **Revision 1, 27 November 2026.**
- **Why:** D-07's second read of SV4 B1, before PR60 merges, with two findings in words you gave or will give (B1C1R-1 for D24, B1C1R-2 for AN3 and AN7).
- **Where the result goes:**
  - your report, in `docs/continuity/dev-manager/reviews/`;
  - App Manager 13's disposition, in the review log under "DM-103";
  - any words you give, applied as given: before the merge where they change a sentence PR60 carries, otherwise in the brief's next revision before B2's prompt.
- **Stream variables:** none are needed.
- **If no report arrives:** PR60 does not merge, and App Manager 13 asks Nathan whether Dev Manager 7's session is available.
- **Deletion condition:** prune once the review log holds DM-103's disposition and PR60 has merged.

**Manager:** before giving this message to Nathan, replace every `<RECORDS_COMMIT>` with the full SHA of the manager-branch commit that holds this revision.

---

**DM-103: SV4 B1's pre-merge read (PR60), with B1-C1 and its exact-head review.** From App Manager 13, relayed by Nathan to Dev Manager 7. Read at commit `<RECORDS_COMMIT>` of `claude/magical-wozniak-yfmmx2`. `main` is at `988a36a`.

Work as your charter says:
- read-only: your report file only, on `claude/dev-manager`;
- no call to Stream, a database, HDE, Railway, Cloudflare or TypeSafe;
- check environment variable names only.

**Where it stands.**
- **PR60** carries SV4 B1 into `main`: F12's surface (D16 to D20, D29's B1 cases, D31), corrected by B1-C1 in DM-102's form (b). The code stands at B1-C1's head `48f0801`; every later commit is Markdown. The brief is at revision 13.
- **The reviews,** all in the SV4 record (`docs/testing/evidence/2026-11-19-sv4-chat-notifications.md`), each with the manager's disposition:
  - **B1's exact-head review** (from `9bf7141`): changes requested. B1R-1 to B1R-3 were the token's custody; B1R-4 to B1R-9 were nits or carries. Your DM-102 decided B1-C1's design.
  - **B1-C1** (code head `48f0801`; run of record 45941121120, twelve jobs, the chat suite 37/37): the manager verified it and merged it at `4185119`, with AN9 and AN10. The session recorded two judgments: the handle's re-read under concurrency, and the four earlier cases' lookup (item 4).
  - **B1-C1's exact-head review** (from `47ecc48`): **approve with nits.** Nothing blocking and no correction pass; B1C1R-1 is a should-fix in the manager's notes for B2, and B1C1R-2 to B1C1R-6 are nits.
  - **PR60's run** 45944433576 (`pull_request`, `47ecc48`) passed all twelve jobs, and the gate printed "Application checks passed".
  - **Codex** reviewed `47ecc48` with no findings. Its two P2 threads (4713760650 and 4715163584) are outdated and unresolved; the review found each answered by the code at `48f0801`.
- **Governing Markdown:** `git diff --name-only 988a36a <RECORDS_COMMIT> -- AGENTS.md CLAUDE.md '**/AGENTS.md' '**/CLAUDE.md' docs/pf-canon docs/planning/manager-workflow.md docs/planning/dev-manager.md docs/operations/ci-and-branch-policy.md .claude .github` prints nothing. PR60 changes no governing file and no workflow.

**Give a verdict on each item:** approved, approved with conditions, changes requested, declined, or refer to Nathan. Where a condition changes text, please give the words (AM9-08). New labels start at AO.

**1. B1 and B1-C1 as settled.** Read the record's sections "B1", "Manager verification of B1", "Exact-head review of B1", "Dev Manager 7's DM-102", "B1-C1", "Manager verification of B1-C1" and "Exact-head review of B1-C1". At `48f0801`:
- F12's three sealed routes hold, with D19's codes and the installation from the header only;
- the transfer, the bound and the locks hold;
- custody holds as AN1 says, its exception being a process stop, or a failed handle write and a failed discard, between the `put` and the handle;
- the seal and HDE's boundary are unchanged.

**Asked:** anything B1 or B1-C1 settled that you would not approve before the merge.

**2. B1C1R-1: the sweep's rules for D24.** The review found AN2 incomplete for B2. These four rules are now in the carried-items file's entry from B1-C1's review:
- **(a)** the sweep discards only a reference whose row its own delete removed. In the review's probe P3, a save that commits first leaves the sweep's delete removing no row; a sweep that discarded anyway would destroy a live token.
- **(b)** it takes no account, session or registration lock while it holds a pending row.
- **(c)** every writer of a non-null `token_secret_ref` consumes that reference's handle, which `_held_since` relies on.
- **(d)** it writes a row again under a new key.

B1C1R-4 adds how a failed re-read's row ends: probe P1 removed such a row without a discard, and the holder's revoke then succeeded.

**Asked:** the words for D24 (the brief's "pending discards' retry" bullet, AN2's sentence). The manager proposes applying them in the brief's next revision before B2's prompt, so they do not hold this merge. Say if they should land before it.

**3. B1C1R-2: AN3's and AN7's words.** B1-C1's code leaves the handle after a failed re-read (`_held_since` raising). That is a known outcome that saved nothing, and the safe choice, since the reference may be another holder's. The custody sentences you gave say a known outcome that did not save discards at once:
- AN3, in `production-contracts.md`'s custody bullet;
- AN7, in `data-model.md`'s `PendingTokenDiscard` row.

The adapter's custody paragraph and `PendingTokenDiscard`'s docstring say the same; those are code, and carried to B2. B1C1R-6, a nit the manager carries, is the related point that a failed write may leave its row.

**Asked:** words for AN3 and AN7 to apply before the merge (Markdown only), or carry them to B2 with the docstrings.

**4. The manager's D-07 calls since DM-102.**
- **B1-C1's two judgments,** accepted at the verification without a consultation:
  - **the handle in two statements** (the conditional insert and `_held_since`'s re-read) implements AN1's "only if no registration and no pending discard already holds that reference" under concurrency. It changes no design, model or lock order. The review found the race real, and the re-read the thing that closes it.
  - **the four earlier cases' lookup by the store's issue order** was a change the prompt's stop rule made a stop. The prompt's "nothing else in those cases changes" could not hold (AM13-18), and the change finds the same reference another way. The review checked all nine calls.
- **The review's dispositions:** no correction pass; B1C1R-1, B1C1R-3, B1C1R-4 and B1C1R-6 carried to B2; B1C1R-5 fixed in the carried-items file; B1C1R-2 to this read.

**Asked:** agree, or say which belonged otherwise.

**5. Codex's two P2 threads.** **Proposed:** the manager resolves them after this disposition and before the merge. Each is answered by the code at `48f0801`, and Codex's review of `47ecc48` found nothing. **Asked:** agree.

**6. Carried and recorded:** the carried-items file's entries from B1's record, B1's review and B1-C1 (for SV4 B2, P08, P09, P11B); the P11 plan's B1R-4 entry; AN9 and AN10 as applied. **Asked:** anything misplaced, or anything to fix before the merge.

**7. Records since DM-102.**
- `d0838ad`: your report merged.
- `f7a21b9`: revision 13 (AN1 and AN2 as given, B1-C1's owned paths), B1-C1's prompt, and AM13-16 and AM13-17.
- `4185119`: B1-C1's merge.
- `47ecc48`: the manager's verification, AN9 and AN10, B1-C1's limits carried, B1-C1's review prompt, and AM13-18.
- `<RECORDS_COMMIT>`: the review's record and disposition, the carries, and AM13-19 and AM13-20.

**Asked:** confirm, or report a mismatch.

**8. Notion.** Please report any mismatch you find at `<RECORDS_COMMIT>`, including the Dev Manager page's DM-102 and DM-103 rows.

**The merge, as proposed:**
1. This read is disposed, and any words for this merge are applied as given (Markdown only).
2. That head's PR run passes all twelve jobs, with "Application checks passed".
3. Codex completes on that head.
4. The two threads are resolved, and PR60's checklist is filled.
5. The merge, its receipt, and the branch cleanup (B1's and B1-C1's branches).
6. Then B2's design revision and its prompt.

**Nathan:** nothing in this read is expected to need him.

**Please end your answer with the relay message for Nathan, naming your report file and the commit on `claude/dev-manager`.**
