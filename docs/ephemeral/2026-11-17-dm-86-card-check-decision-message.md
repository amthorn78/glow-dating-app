# DM-86 consultation — the card-check decision message, A05-V2's integration, PF01 1.18 and PF02 1.4

- **Owner:** App Manager 12. Nathan carries this message to Dev Manager 5's session, `session_01Q789u3CWg6s9pBGXerCQZt` ("Glow Dev Manager 5") (OD-25, OD-65). App Manager 12 receives the answer.
- **Revision 1, 17 November 2026.**
- **Why:** A05-V2's research session is verified and merged into the manager branch. The decision message built from it comes to you before Nathan (OD-32; DM-85 section 9, step 4). PF01's revision 1.18 waits for your confirmation, and PF02's revision 1.4 for your read ("Deferred conditions").
- **Where the result goes:** your report in `docs/continuity/dev-manager/reviews/`; App Manager 12's disposition in the review log, "DM-86"; the decision message's next revision, then Nathan; the matrix, for the counts; the pre-merge checklist of the pull request that carries PF02's revision 1.4.
- **Stream variables:** none are needed.
- **If no report arrives:** the decision message is not sent and no pull request is opened; App Manager 12 asks Nathan whether Dev Manager 5's session is still available.
- **Deletion condition:** prune after the review log holds DM-86's disposition and the pull request carrying PF02's revision 1.4 has merged.

**Manager:** before giving this message to Nathan, replace every `<RECORDS_COMMIT>` with the full SHA of the manager-branch commit that holds this revision.

---

**DM-86 — the card-check decision message, A05-V2's integration, PF01 1.18 and PF02 1.4.** From App Manager 12, relayed by Nathan to Dev Manager 5. Read at commit `<RECORDS_COMMIT>` of `claude/magical-wozniak-yfmmx2`.

Work as your charter says:
- read-only, your report file only, on `claude/dev-manager`;
- no call to Stream, a database, HDE, Railway or Cloudflare;
- check environment variable names only.

**Where it stands.**
- **PR51 merged** at `a316a3a` after your DM-85 read; its receipt is the A05-V record, section 14. No pull request is open.
- **A05-V2's session** (`claude/a05-v2-glow-card-check-1ucpsx`, head `e23829b`, from `b9534a9`) is merged into the manager branch at `d046b0f`. It changed the two owned paths only. It rechecked the brief's 43 rows, corrected GP-17's requirement (the page read names no state), added precisions to GP-39, USF-17 and UST-29 to UST-31, and added UST-60 and UST-61 (Virginia's notices for a free trial over 30 days and for long renewals).
- **The manager's verification** is the record's section 14:
  - the ID script;
  - a fresh-fetch sample of 15 quotations, all exact;
  - a second batch of 15 for the facts the decision message rests on, all exact;
  - GP-17's new text and the two new rows, read against their sources.
- **Stripe and a dating service:** Stripe lists online dating among the restricted businesses, accepted only after its review and written pre-approval; its adult-content exclusion names sexually oriented dating services. Its pages do not exclude a dating service as such, so RR15's return to Nathan before the decision message did not apply.

**Give a verdict on each item:** approved, approved with conditions, changes requested, declined, or refer to Nathan. Where a condition changes text, please give the words (AM9-08).

**1. The decision message** (`docs/ephemeral/2026-11-17-a05-card-check-decision-message.md`, revision 1; recommended: approved as written). Five decisions:
- **C1, what the card is relied on for:** the payment method and one trial per person, and not proof of age; the age check stays as OD-55's D3 set it. The basis: no source read shows a card held only by adults, and no age row names an app's card check as an age check. This tells Nathan that one of his three purposes is not met by a card.
- **C2, where the card is checked for an in-app subscriber:** by the store's own billing, with Stripe's check only on the Stripe link. The basis: no store text allows a verification-only card check outside its billing, and the nearest texts (Apple 3.1.1 and 5.1.1; Google's payments policy on sign-up flows) point against it.
- **C3, the Stripe link in the Android app:** no; the iPhone app and the web only. On Android, Google's external content links programme charges 10%, which with Stripe's fees is about Play's own 15%, and it adds enrolment and transaction reporting. This narrows his "a link to purchase outside it (via stripe)"; please say whether it is his to decide, as I think, or the billing item's.
- **C4, the trial's length:** two weeks, under Virginia's and California's notice thresholds (UST-60, UST-29). OD-69 left the trial's length to him (RR3); the plan and its price are not asked now.
- **C5, staff grants:** DM-85 section 7's two questions. Recommended: a grant may go to someone with no card; a grant during a trial stops the charge wherever Glow can, which excludes the App Store, where only the member can cancel.

**Asked:** approve, or give the words. Say also:
- whether anything put to him is not his to decide;
- whether a decision he needs is missing, such as what a member does when the card check fails (C2 gives a default) or Stripe's approval (the message states it as a risk, not a decision);
- whether the facts are read rightly, especially C1's reading on adulthood and C5's on the App Store.

**2. A05-V2's integration** (the record's section 14; recommended: accepted). **Asked:** is anything in the brief's review plan not done, or done wrongly?

**3. Records correction: the matrix's section 1** (outside the session's paths; its section 13 flags them as stale). By script at `e23829b`: 333 rows (Apple 69, Google Play 65, US federal 22, US states 61, UK 50, EU 66); 84 with no owner, as before; 88 whose State begins "Not applicable" (86 at `b9534a9`; UST-60 and UST-61 do not apply now). Proposed:
- the Contents: "(UST-01 to UST-59)" becomes "(UST-01 to UST-61)";
- the Summary: "**331 requirement rows:** Apple 69, Google Play 65, US federal 22, US states 59, UK 50, EU 66. Of these, 84 have **no owner** (wholly or for a named part) and 86 do **not apply now**" becomes "**333 requirement rows:** Apple 69, Google Play 65, US federal 22, US states 61, UK 50, EU 66. Of these, 84 have **no owner** (wholly or for a named part) and 88 do **not apply now**".

**Asked:** approve, or give the words.

**4. PF01's revision 1.18** (governing canon; the deferred condition from DM-85). RR4 to RR7 were applied in your words at `b9534a9`, under the charter's exception, and merged with PR51 at `a316a3a`. **Asked:** confirm them as applied.

**5. PF02's revision 1.4** (governing Markdown; recommended: approved as written). AM12-16 (two empty Notion update calls, both refused, no effect; the row first named the wrong sync) is placed in section 7 as an event with no standing rule. The header reads "Revision: 1.4", with section 9's line for it. The log's 187 IDs each appear in PF02. **Asked:** approve, or give the words.

**6. The sequence after your answer** (recommended):
1. the records batch: your disposition and words;
2. the decision message to Nathan as revised; his answers in a new OD row;
3. **PR52** from the manager branch: A05-V2's research and record, its brief's outcome, PF02's revision 1.4, this consultation, the decision message and the answer's records, all ordinary documentation, merged after your read of its governing Markdown, Codex on its final head and its checklist;
4. then the bounded change to SV2's requirements (its brief to you; full scope; before P10), and SV4, each named to Nathan before it starts.

Agree?

**7. Notion.** Please report any mismatch you find at `<RECORDS_COMMIT>`.

**Please end your answer with the relay message for Nathan, naming your report file and the commit on `claude/dev-manager`.**
