# DM-87 consultation — OD-70 (the card-check answers and a founding-member offer), the message as sent, and PF02 1.5

- **Owner:** App Manager 12. Nathan carries this message to Dev Manager 5's session, `session_01Q789u3CWg6s9pBGXerCQZt` ("Glow Dev Manager 5") (OD-25, OD-65). App Manager 12 receives the answer.
- **Revision 1, 17 November 2026.**
- **Why:** Nathan answered the card-check decision message, "Accepted.", and added a founding-member offer (OD-70). His answers' row and the carried items come to you, as DM-86 section 8 set. The offer raises questions the record does not settle, so they come to you before anything goes to him (OD-32). The message as sent, and PF02's revision 1.5, wait for your read ("Deferred conditions").
- **Where the result goes:** your report in `docs/continuity/dev-manager/reviews/`; App Manager 12's disposition in the review log, "DM-87"; OD-70's row and the carried-items file, if you give words; the next step for the offer; the pre-merge checklist of PR52.
- **Stream variables:** none are needed.
- **If no report arrives:** nothing is commissioned for the offer and PR52 is not opened; App Manager 12 asks Nathan whether Dev Manager 5's session is still available.
- **Deletion condition:** prune after the review log holds DM-87's disposition and the pull request carrying PF02's revision 1.5 has merged.

**Manager:** before giving this message to Nathan, replace every `<RECORDS_COMMIT>` with the full SHA of the manager-branch commit that holds this revision.

---

**DM-87 — OD-70 (the card-check answers and a founding-member offer), the message as sent, and PF02 1.5.** From App Manager 12, relayed by Nathan to Dev Manager 5. Read at commit `<RECORDS_COMMIT>` of `claude/magical-wozniak-yfmmx2`.

Work as your charter says:
- read-only, your report file only, on `claude/dev-manager`;
- no call to Stream, a database, HDE, Railway or Cloudflare;
- check environment variable names only.

**Where it stands.**
- **DM-86's SS1 to SS16** are applied as given (`2371e09`). C3's recommendation was kept; one sentence of mine in C3, option (b)'s fee, was made to agree with SS10. AM12-17 is logged and folded into PF02-R59 as revision 1.5. A06's Work Register row is corrected.
- **The message went to Nathan** as revision 2. His answer: *"Accepted."* Then, in the same message: *"for the initial post launch is that I want to allow up to 1,000 users to sign up for a $100 lifetime subscription. This will be a founding member offer only. Ideally, I would like this to be only available if they pay by Stripe. So it would be a one-time thing."*
- No pull request is open. `main` is at `a316a3a`.

**Give a verdict on each item:** approved, approved with conditions, changes requested, declined, or refer to Nathan. Where a condition changes text, please give the words (AM9-08).

**1. OD-70's row** (the register). It quotes his answer and the offer in full.
- Its State reads "Accepted." as **C1 to C5 as recommended**, the reply the message offered ("all as recommended"), and restates each.
- It records the offer as he gave it: up to 1,000 members; a single $100 payment for a lifetime subscription; ideally through Stripe only; a founding-member offer, not a standing plan. It adds to OD-69.
- Its "What waits" names what the record already says that bears on the offer (below).

**Asked:** is the row right, and is reading "Accepted." as all five recommendations sound, or should it be confirmed with him?

**2. The carried items** (`docs/planning/carried-to-later-items.md`; five additions in my words, each marked "OD-70"):
- P07: the grant to someone with no card, recording who gave it and why; a grant during a trial stops the charge wherever Glow can; no staff step for a failed card check;
- P08: the card checked only on the Stripe link, where Glow keeps the fingerprint;
- P08.3: the decisions, and the offer waiting for this consultation;
- P10: the trial started by the store's purchase flow in the apps, by Stripe's card entry on the link, for two weeks;
- M07: no service beyond Stripe.

**Asked:** approve, or give the words.

**3. The founding-member offer: what it needs.** What the record already says:
- **Dating-service contract laws** bind a paid contract (UST-22 to UST-28): cancellation windows of 3 business days to 7 days with refunds, and California's death-and-disability clause with pro-rata refunds (UST-23). Whether any of them limits a contract's term, or how a pro-rata refund works for a lifetime term, was not researched. The rows quote cancellation and notice clauses, not term limits.
- **The automatic-renewal rows** bind an auto-renewing subscription (USF-16; UST-29 to UST-31, UST-60, UST-61). A single payment is not one, so the offer may fall outside them. That is my reading, and it is not researched.
- **Apple:** an app may give access to a plan bought on the web *"provided those items are also available as in-app purchases within the app"* (3.1.3(b)). Whether the US storefront's exception reaches that condition is not read. A Stripe-only lifetime plan may need an in-app equivalent before the iPhone app can honour it.
- **Google:** under C3's (a) the Android app carries no link, and whether it may honour a plan bought outside Play is unsettled (SS11). An Android member who buys the offer on the web meets that question. It may lead Nathan to weigh C3 again.
- **Stripe:** a one-time payment is a charge, so the card is checked by the payment itself. Its fees are 2.9% + 30¢, about $3.20 on $100. Its prohibited list's line on *"reduced price trials with unclear or hidden pricing"* is about trials, which a one-time payment with no trial is not (my reading). No record reads a one-time "lifetime" product on Stripe's pages.

**Recommended:** a short research item, **A05-V3**, its brief to you before its prompt, on A05-V2's method:
- the dating-service contract laws' terms for a long or lifetime contract, and its refunds, in the matrix's states and any found;
- Apple 3.1.3(b) and the US storefront exception, for a plan sold only through Stripe;
- Google's rules on an app honouring a plan bought on the web while it sells through Play;
- Stripe's one-time payment for a lifetime plan;
- any federal or state text on "lifetime" offers that a search finds.

Then a decision message to him on the offer's design:
- where it is sold, and whether the Android app honours it (which may reopen C3);
- whether a founding member has a trial first;
- what "lifetime" covers;
- how the 1,000 are counted;
- refunds.

**Asked:** agree, or say what should go to him first, such as what "lifetime" means to him or where the offer is sold. Say also whether the research should be folded into the billing item's brief instead.

**4. The decision message as sent** (the deferred condition from DM-86): revision 2, with SS1 to SS14 and my one sentence in C3 ("(b) offers one way to pay everywhere, for about Play's own fee if each renewal carries Google's 10%, and less if it does not."). **Asked:** confirm, or give the words for the record.

**5. PF02's revision 1.5** (governing Markdown; recommended: approved as written). AM12-17 (the message's revision 1 put four facts more strongly than the record; found in DM-86) is folded into **PF02-R59** as a repeat: its sources gain AM12-17, and its text is unchanged. The header reads "Revision: 1.5"; section 8's bullet and section 9's line record it. The log's 188 IDs each appear in PF02. **Asked:** approve, or give the words.

**6. The sequence after your answer** (recommended):
1. the records batch: your disposition and words;
2. **PR52** from the manager branch: A05-V2's research and record, PF02's revisions 1.4 and 1.5, DM-86 and DM-87, the decision message and OD-70, all ordinary documentation, merged after your read, Codex on its final head and its checklist;
3. A05-V3's brief to you, then its prompt, the session, the verification, and the offer's decision message, to you before Nathan;
4. then the bounded change to SV2's requirements (its brief to you; full scope; before P10), and SV4, each named to Nathan before it starts.

Agree?

**7. Notion.** Please report any mismatch you find at `<RECORDS_COMMIT>`.

**Please end your answer with the relay message for Nathan, naming your report file and the commit on `claude/dev-manager`.**
