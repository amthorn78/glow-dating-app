# A05-V3 — Research for the decision on the founding-member offer

- **Work ID:** A05-V3, under A05 and A06. Source: OD-70 (Nathan, 17 November 2026) and DM-87 section 5.
- **Owner:** a research session started by Nathan. **Manager:** App Manager 12.
- **Starting commit:** the commit of the manager branch `claude/magical-wozniak-yfmmx2` named in the prompt.
- **Revision 2, 18 November 2026,** with DM-88's UU1 to UU7 applied as given (Dev Manager 5, `dde5216`, a read of `e2973ee`). Revision 1 went to the Dev Manager in DM-88. Status: approved; the prompt follows.

## Why

Nathan has added a founding-member offer after launch (OD-70):
- up to 1,000 members may buy a **lifetime subscription for $100, paid once** (the manager's reading of his "a one-time thing");
- **ideally only through Stripe**;
- it is a founding-member offer, not a standing plan. OD-69's paid plan, its two-week free trial and the staff grants stand beside it.

The record does not settle what the offer needs (DM-87 section 5):
- the dating-service contract laws bind a paid contract (UST-22 to UST-28), but their rows quote cancellation and notice clauses only, and no row names a contract's term;
- California's death-and-disability relief clause (UST-23) is quoted only at its start, and the row's "Asks of Glow" cell, "The clause; pro-rata refunds", summarizes refund terms its quotation does not show;
- New York's rules on deleting a paying member's material "when the contract ends" (UST-25) and its Bill of Rights "at each sale or renewal" (UST-24) assume an end and renewals;
- Apple lets an app give access to a plan bought on the web *"provided those items are also available as in-app purchases within the app"* (3.1.3(b)), and whether the US storefront's exception reaches that condition was not read;
- under OD-70's C3 the Android app carries no Stripe link, and whether it may honour a plan bought outside Google Play is unsettled (DM-86, SS11);
- whether the automatic-renewal rows reach a single payment was not read.

The decision message that puts the offer's design to Nathan needs those facts first.

## Outcome

**1. The matrix recheck** (DM-37 5.1; the matrix's section 10), on A05-V2's method. Each row's source is re-read today, its date updated, its quotation found in the text read, and its ID kept. A row whose requirement has changed is corrected in place and marked as rechecked; nothing is deleted.

| Group | Rows | Why |
|---|---|---|
| Dating-service contract laws | UST-08; UST-22 to UST-28 | Whether a contract measured by the member's life, or longer than a set term, is allowed; payment periods; refunds; when a lifetime contract "ends" |
| Automatic renewal and federal consumer law | USF-13, USF-16, USF-17; UST-29 to UST-31, UST-60, UST-61 | Whether any reaches a single payment for a lifetime plan; what the FTC Act asks of a "lifetime" claim |
| The stores' purchases and external links | AP-39 to AP-42; GP-38, GP-39, GP-41, GP-42 | What a lifetime purchase is in each store, its fee, and whether an app may honour a plan bought outside the store. AP-40 and GP-42 are each store's subscription rules, which an in-app lifetime plan would sit under or outside if 3.1.3(b) or a reopened C3 puts one in an app |

The session also searches primary sources for **state dating-service contract laws not already in the matrix**, and for **federal or state texts on "lifetime" memberships or contracts**, wherever a matrix row or a search finds them. A law already in a row is rechecked in that row, not added again. Each one found in a primary text becomes a new row with the next free ID in its section (the matrix's section 1: IDs are added, never reused), marked as added at this recheck. Each search that finds none is recorded as searched, with the sources tried.

**2. Four questions of fact, each from primary sources read today** (DM-87 section 5):
- **A term or a life measure.** Whether any dating-service contract law bars a contract measured by the buyer's life, or caps a contract's term or its payment period. Read each statute's full text for UST-08 and UST-22 to UST-28, not only the quoted clause.
- **Refunds, read whole.** UST-23's death-and-disability clause in full, and any relocation, closure or cancellation refund in these laws, for prepaid services not yet received. How each one's text applies to a contract with no end date, quoted as found and not resolved by the session. UST-23's "Asks of Glow" cell ("The clause; pro-rata refunds") is quoted from the statute or corrected.
- **When a lifetime contract "ends".** What New York's GBL §394-c says about the end of a contract, renewals and the Bill of Rights for a single sale (UST-24, UST-25), and what any other law read says about a contract with no end date.
- **The stores.**
  - **Apple:** whether 3.1.3(b)'s proviso applies on the US storefront when the plan is sold only through a link (AP-42). What an in-app lifetime plan would be (a non-consumable or non-renewing purchase), and Apple's commission on it; A05-V2's record has the 70% and 85% for auto-renewing subscriptions only.
  - **Google:** whether an app that sells through Play may give access to a plan bought on the web, or through the external content links programme (GP-38, GP-39; answers 10281818 and 9858738). Its fee on a one-time item bought through a link. A05-V2's record has 10% for other in-app items on the first US$1M; recheck it.

**3. Stripe's one-time payment.** From Stripe's own pages:
- a single payment for a product with no renewal (Checkout in payment mode);
- what the payment itself checks about the card;
- its fees;
- refunds and disputes on a one-time payment, and any time limit on them;
- any Stripe term on "lifetime" products or prepaid services;
- whether a payment can be limited to buyers in the US, the launch country for now (OD-55), and how.

**4. A facts table for the decision message,** each cell citing the rows and pages that bear on it, with no recommendation:
1. where the offer can be sold (the web, the iPhone app's link, the Android app), and what each store asks for it to be honoured in the app;
2. whether a founding member's purchase is touched by the free trial's rules, the automatic-renewal laws or the dating-service contract laws;
3. what "lifetime" can mean under the laws read, and what they say when the service ends;
4. what a founding member can get back, and when;
5. what each channel costs on $100;
6. anything the laws or the stores say about a limited number of buyers or a "founding" offer, or nothing found.
7. how a member already in a free trial (OD-69) moves to the offer in each channel without a second charge, given that in the App Store only the member can stop a trial's charge (OD-70, C5).

## Owned paths (the session)

- `docs/planning/store-legal-safety-requirements.md`: the rechecked rows, their dates, any new rows, the Rows columns of sections 7 and 8 where a row is added, the header's Rechecks entry for this recheck, and each sentence of sections 9 and 10 that states a rechecked row whose requirement or status changed, corrected and marked as corrected at this recheck.
- `docs/testing/evidence/<the session's date>-a05-v3-founding-member-offer.md`: the session's record (method, sources with their hashes, the quotation checks, the four questions, Stripe's one-time payment, the facts table, deviations and limits).

## Manager-owned

This brief; the prompt; the carried-items file; the handoff; the owner-direction register; the review log; PF01; the decision message.

## Exclusions

All code, configuration, workflows and other Markdown. No account, sign-up, test-mode key, API call, form, sales contact or message to Stripe, a store, a regulator or anyone else. No call to Stream, a database, HDE or Railway. No statement that Glow is, or would be, compliant (DM-37 1.1), and no legal conclusion: where a text's application to a lifetime contract is unclear, the record quotes it and says so. No plan, price or offer term is proposed: those are Nathan's (A06; OD-70). The UK and EU rows are not read: the launch country is the US, all states, for now (OD-55). If the offer were sold to buyers in the UK or the EU, the rows there that bind a paid contract would bear on it, among them the 14 days to cancel (UK-46, EU-57).

## Dependencies and inputs

Public web pages and official statute sites only. The session reads OD-69 and OD-70 in the owner-direction register; DM-86 section 3, DM-87 sections 3 and 5, and DM-88 section 3 (which corrects DM-87 section 3 on UST-23's "Asks of Glow" cell); the A05-V2 record (`docs/testing/evidence/2026-11-17-a05-v2-card-check-and-paid-trial.md`), sections 1, 4, 7, 8, 10 and 14, for its method and its store and Stripe facts; and the matrix's sections 1, 8, 9 and 10.

## Acceptance checks

- `git diff --name-only <START_SHA> HEAD` prints only the two owned paths.
- Every row ID present at `<START_SHA>` is present at the head, in the same order (A05-V's script).
- Every rechecked row's Source cell carries `rechecked <today> (A05-V3)`, or the record names it as not re-read, with the reason.
- Each rechecked row's quotation is found as one continuous string in the stripped text of the source read today; the record's table lists each row, its source's SHA-256 and the result.
- Each fact for the four questions and for Stripe names its page and the date read; each new row names its primary text and the rows it was compared with.

## Classification expectation

`ordinary-docs-only`: both owned paths are Markdown, outside any `.claude/` directory.

## Evidence home

The session's record; the manager's verification is added to it as a section.

## Report format

Branch, start and head SHAs, changed paths, the rows rechecked (with any changed requirement named), the rows added, the four questions' and Stripe's findings in short, the sources unread with their URLs, every acceptance check with its exact result, deviations and open questions.

## Review plan

The change is Markdown only, so no code review applies. The manager verifies: the ID script; a sample of the quotation checks re-run from fresh fetches; every changed requirement and every new row read against its source; each corrected sentence of sections 9 and 10 read against its row. The decision message built from the record goes to the Dev Manager before Nathan.

## Sessions

None yet.
