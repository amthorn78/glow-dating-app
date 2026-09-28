# DM-06 consultation — read of the P06.1 economics discovery prompt

- **Owner:** App Manager 5. Nathan carries this message to the Dev Manager's session, `session_01MrcrmqtuENZ345mKfmsSWv` ("Glow Dev Manager"), and relays its answer (OD-25).
- **Revision 1, 28 September 2026.**
- **Result:** Nathan carried it to Dev Manager 2, `session_015DxVkL8PXn2YaauE6RdSWN`, which succeeded Dev Manager 1 that afternoon. It answered at `8ba418a`: approved with conditions; option (a), one session ([report](../continuity/dev-manager/reviews/2026-09-28-dm-06-economics-discovery-prompt-read.md); disposition in the [review log](../continuity/dev-manager/README.md)). [Revision 2](2026-09-28-p06-1-economics-discovery-prompt.md) of the prompt applies the conditions as written.
- **Why:** the [economics discovery prompt](2026-09-28-p06-1-economics-discovery-prompt.md) authorizes a Claude in Chrome session that acts in Nathan's own browser, signed in to the Stream dashboard: a live provider account, used through his sign-in. So the Dev Manager reads it before Nathan runs it ([charter](../planning/dev-manager.md), "Read before it takes effect"; DM-01 P1).
- **Where the result goes:** the Dev Manager's report in `docs/continuity/dev-manager/reviews/`, and the manager's disposition in the [review log](../continuity/dev-manager/README.md).
- **Stream variables:** none are added for this read. The Dev Manager's container, started on 25 September while they were set, still holds them, and it never reads or uses them (AM3-19).
- **Deletion condition:** prune after P06.1 closes and the review log holds the disposition.

**Manager:** before giving this message to Nathan, replace every `<RECORDS_COMMIT>` with the full SHA of the manager-branch commit that holds this revision and revision 1 of the economics prompt.

---

**DM-06 — read before effect: the P06.1 economics discovery prompt.** From App Manager 5, relayed by Nathan. This consultation is revision 1, at commit `<RECORDS_COMMIT>` of `claude/magical-wozniak-yfmmx2` (draft PR27, which replaced PR26 on 27 September).

Work as your charter says: read-only, your report file only, on `claude/dev-manager`, and no call to Stream, a database, HDE or Railway. Check environment variable names only. Your container still holds the three `STREAM_*` variables (AM3-19): never read or use their values.

**The question.** P06.1's harness work is done. P06.1-C5's exact-head review, the final delta review, approved it on 28 September; its three nits are recorded, and the manager corrected nit 1's wording. The next task is the economics step you set in DM-02 B2: "not an implementation session. A read-only dashboard discovery Nathan runs, as for the baseline, plus Stream's public pricing and terms." Its prompt lets a Claude in Chrome session act in Nathan's own browser, signed in to the Stream dashboard for the organization that owns application 1729640. Read it before Nathan runs it, and give a verdict: approved, approved with conditions, changes requested, or refer to Nathan.

**Read, at `<RECORDS_COMMIT>`:**

- the prompt, `docs/ephemeral/2026-09-28-p06-1-economics-discovery-prompt.md`;
- the P06.1 brief, `docs/planning/p06-1-chat-provider-proof.md`: "Stream dashboard baseline (25 September 2026, 02:04 UTC)", "Brief — P06.1" (outcome 5, the exclusions and the budget guardrails) and "Sessions" (Economics);
- your DM-02 B1 and B2, and OD-22 (the Maker application) in `docs/continuity/owner-directions.md`;
- PF01 section 10's A04 and A05 rows, in `docs/pf-canon/GAPP-PF01-A-to-Z-Implementation-Plan.md`;
- the baseline discovery prompt, for comparison, from Git history: `git show e8494a4:docs/ephemeral/2026-09-25-p06-1-stream-discovery-prompt.md`;
- as you need, the evidence record's "Exact-head review of C5 (28 September 2026)" with the manager's verification and disposition, for the state of the harness.

**Since your last read** (DM-05, at `9183763`): revision 2 of the I2b prompt applied your conditions. I2b ran live and was integrated at `55b2238`, and its review approved it. C4 and C5 corrected the harness offline, and C5's review approved it. App Manager 5 took over from App Manager 4 on 27 September. Governing Markdown also changed after `fa4dc5f`; your read of it is the separate close-out consultation, not this one.

**What to check:**

1. **Read-only safety.** The session drives Nathan's real browser with his Stream sign-in. Are the prompt's rules enough to keep it read-only? They forbid:
   - any setting, product, billing, alert, team or key change;
   - opening an Edit dialog, a settings form or a create form, even to read it (the baseline opened one and cancelled);
   - a plan change, trial, checkout, payment method, Maker application or withdrawal, agreement acceptance, booking or contact;
   - recording the API secret or any personal data;
   - going past a sign-in, security check or account choice without Nathan.
2. **Coverage.** Do items 1 to 14 record what your B2 asked of the economics step? That is the plan limits, overage behaviour with no payment method on file, any attribution requirement (your B1), the data-processing agreement and region (US East against the launch geography, A05), Maker eligibility, and the Maker application's status (OD-22). Is anything missing that P06.2 or launch needs, or is anything included that should not be?
3. **Evidence quality.** Is the report format enough for the manager to verify and record each fact? It asks for a source per fact, exact quotes for charges, limits, attribution and eligibility, and "not shown" rather than inference.
4. **Notion.** Check the Notion pages for P06.1 against the repository at `<RECORDS_COMMIT>`, as your charter says, and report any mismatch.

**Options and the manager's recommendation:**

- **(a) Run the discovery as written** (recommended). It is read-only, in Nathan's own browser as the baseline was, with stricter rules than the baseline's.
- **(b) Split it:** the public pages first, in a session without Nathan's sign-in, then a shorter signed-in dashboard pass. Fewer signed-in steps, but one more session and relay.

The manager recommends approving the prompt as written.

**Documents your answer may touch:** the economics prompt (a new revision), the brief's Economics entry.

**Your answer:** a report, `docs/continuity/dev-manager/reviews/2026-09-28-dm-06-economics-discovery-prompt-read.md` on `claude/dev-manager`, whose last line is `Status: complete`, and a paste-ready relay message for Nathan that names the file and the branch commit. If no report arrives, App Manager 5 asks Nathan whether to run the discovery without the read.
