# DM-04 consultation — read of the P06.1-I2a prompt

- **Owner:** App Manager 3. Nathan carries this message to the Dev Manager's session, `session_01MrcrmqtuENZ345mKfmsSWv` ("Glow Dev Manager"), and relays its answer (OD-25).
- **Revision 1, 26 September 2026.**
- **Why:** the [I2a prompt](2026-09-26-p06-1-i2a-implementation-prompt.md) authorizes credential use and live provider actions, so the Dev Manager reads it before Nathan runs it ([charter](../planning/dev-manager.md), "Read before it takes effect"; DM-01 P1).
- **Where the result goes:** the Dev Manager's report in `docs/continuity/dev-manager/reviews/`, and the manager's disposition in the [review log](../continuity/dev-manager/README.md).
- **None added for this read:** it needs none, and Nathan adds them only for I2a itself.
  - **Correction, after the message was given:** its sentence "The Stream variables are not set for this read" was wrong. The Dev Manager's container, started on 25 September while they were set, holds them; it never read or used them (DM-04 finding 10, AM3-19).
- **Result:** approved with conditions, which revision 2 of the I2a prompt applies; see the [review log](../continuity/dev-manager/README.md), "DM-04".
- **Deletion condition:** prune after P06.1 closes and the review log holds the disposition.

**Manager:** before giving this message to Nathan, replace every `<RECORDS_COMMIT>` with the full SHA of the manager-branch commit that holds this revision and revision 1 of the I2a prompt.

---

**DM-04 — read before effect: the P06.1-I2a implementation prompt.** From App Manager 3, relayed by Nathan. This consultation is revision 1, at commit `<RECORDS_COMMIT>` of `claude/stoic-carson-66gdig`.

Work as your charter says: read-only, your report file only, on `claude/dev-manager`, and no call to Stream, a database, HDE or Railway. Check environment variable names only. The Stream variables are not set for this read; if any `STREAM_*` name is present, say so in your report and never read or use its value.

**The question.** P06.1-I2a is the live revocation and safety session your DM-02 B2 specified. Its prompt authorizes the Stream secret and live, destructive actions on the run's own data in application 1729640: bans, suspension, hard deletes and token revocation. Read it before Nathan runs it, and give a verdict: approved, approved with conditions, changes requested, or refer to Nathan.

**Read, at `<RECORDS_COMMIT>`:**

- the prompt, `docs/ephemeral/2026-09-26-p06-1-i2a-implementation-prompt.md`;
- the P06.1 brief, `docs/planning/p06-1-chat-provider-proof.md`: "Brief — P06.1" and "Sessions" (P06.1-I2a);
- the evidence record, `docs/testing/evidence/2026-09-25-p06-1-chat-provider-proof.md`: "Exact-head review of C3", with the manager's verification and disposition, and the three "What P06.1-I2a must know" lists, in C1's, C2's and C3's sections;
- your DM-02 B2 and DM-03 R1 to R3;
- as you need, `proofs/stream-chat/README.md` and the harness.

**Since your last read** (DM-03, at `fa4dc5f`): the I1 review (changes required; S15 confirmed live), the flake fix and its review, and three offline correction passes, C1 to C3, each with an exact-head review that approved it. Governing Markdown also changed after `fa4dc5f`; your read of it is a separate consultation before PR26 merges, not this one.

**What to check:**

1. **Safety of the live actions.** Are these bounds enough: only the run's own data; no application-wide token revocation; the dashboard user never changed or deleted; temporary settings through the run's journal; no `configure --apply` or `restore --apply`; outage injection only on a loopback address where nothing listens; `verify-clean` and the dry-run `configure` before and after; a stop at once on any charge or limit signal; the secret only in the server process's environment?
2. **The run plan,** against the brief's 20-user cap: run 1, the complete set, needs at most 10 users and 15 channels; one targeted rerun is the reserve; nothing else live.
3. **Coverage and claim limits,** against your B2: each mechanism and effect, for both members; suspension and deletion; tokens and devices; send versus revocation on the provider side only (DB06 stays P11's); outage by fault injection only; the S15 mapping; G2 and S10; the endpoints of the I1 review's finding 9; the existence oracle.
4. **The offline first step.** The manager bounded the correction rounds: after C3's review, only a blocking finding, or a should-fix finding that could create a false HOLDS, lose an observed FAIL or send a request after a charge signal, delays I2a. The review found none. So its six nits and one gap go into I2a's offline first step, required where they touch the signal check or a false HOLDS, and I2a's exact-head review covers them. Do you agree, or should a separately reviewed pass come first?
5. **Scope, not tools.** Nathan's direction is to bound implementation sessions' scope, never their tools. Name any line that restricts tools rather than scope.
6. **Notion.** Check the Notion pages for P06.1 against the repository at `<RECORDS_COMMIT>`, as your charter says, and report any mismatch.

**Options for item 4, and the manager's recommendation:**

- **(a) The offline first step inside I2a** (recommended). The items are small, the ones that matter are required before any live call, and I2a's exact-head review covers them.
- **(b) A fourth offline pass and its review before I2a.** Two more sessions for six nits, when the bound exists to stop that loop.

The manager recommends approving the prompt as written.

**Documents your answer may touch:** the I2a prompt (a new revision), the brief's I2a entry, and the disposition of the C3 review in the evidence record.

**Your answer:** a report, `docs/continuity/dev-manager/reviews/2026-09-26-dm-04-i2a-prompt-read.md` on `claude/dev-manager`, whose last line is `Status: complete`, and a paste-ready relay message for Nathan that names the file and the branch commit. If no report arrives, App Manager 3 asks Nathan whether to run I2a without the read.
