# A05-V2 — Research for the decision on the card check and the paid plan's free trial

- **Work ID:** A05-V2, under A05 and A06. Source: OD-68 and OD-69 (Nathan, 17 November 2026) and DM-84 section 4.
- **Owner:** a research session started by Nathan. **Manager:** App Manager 12.
- **Starting commit:** the commit of the manager branch `claude/magical-wozniak-yfmmx2` named in the prompt.
- **Revision 2, 17 November 2026,** with DM-85's RR12 to RR18 applied as given (Dev Manager 5, `05c469d`, a read of `8d272a4`). Revision 1 went to the Dev Manager in DM-85. Status: approved; the prompt follows.

## Why

Nathan has set the MVP's terms (OD-68, OD-69):
- the MVP launches with **a paid plan, and no free plan**;
- **a free trial starts at signup:** the member gives a card then, and the paid plan is charged when the trial ends unless they cancel;
- **free accounts exist only as a staff grant,** never as a default;
- the plan is sold through **the stores' own billing, and by a link to a purchase outside it, through Stripe**;
- **the card check is for three purposes** ("the card is there for all of the above"): a payment method ready for when the trial ends; fake or duplicate accounts made harder; and showing that the member is an adult. Whether a card check can show each is what this research finds;
- no selfie is matched to an ID for the MVP, and the automated photo check is off behind a toggle (OD-68).

How the card check works in each place a member can start the trial, what it can show for each purpose, and what it costs, rest on no source read yet (DM-84 section 4). The decision message that puts the design to Nathan needs those facts. A paid launch also brings in G-07, consumer and subscription law, whose rows were read on 1 November and not rechecked (the matrix's section 10).

## Outcome

**1. The matrix recheck** (DM-37 5.1; the matrix's section 10, whose triggers include a paid launch), on A05-V's method. Each row's source is re-read today, its date updated, its quotation found in the text read, and its ID kept. A row whose requirement has changed is corrected in place and marked as rechecked; nothing is deleted.

| Group | Rows | Why |
|---|---|---|
| The stores' subscriptions and purchases | AP-39 to AP-45; GP-38 to GP-45 | How the stores sell a subscription and its free trial; the US external purchase links (AP-42, GP-39) and their terms |
| Consumer and subscription law (G-07) | USF-16; UST-22 to UST-31 | A free trial that turns into a payment, under federal and state automatic-renewal and dating-service contract laws |
| Age | AP-14; UST-32 to UST-41 | Whether a card check is an age determination any of these rows name or accept |
| Other rows a paid plan switches on | AP-34, GP-08, GP-17; USF-17, USF-20; UST-08 | The matrix marks AP-34, GP-08, GP-17, USF-20 and UST-08 "If paid" (section 1); USF-17 records that the FTC's click-to-cancel amendments were vacated, which bears on what subscription law asks of a trial |

**2. Three questions of fact, each from primary sources read today:**
- **The stores' free trials.** For an auto-renewing subscription with a free trial, on the App Store and on Google Play: whether the store requires a valid payment method to start the trial; what the developer receives about the purchase and the payment method, if anything; how a trial and its conversion are disclosed and cancelled; and the trial lengths each store allows.
- **The stores' rules beyond their billing**, on the US storefront: the terms of a link to a purchase outside the store (fees, reporting, the user's choice, required notices); whether a card check outside the store's billing, used only to verify and never to charge, is allowed when the plan is bought through the store; and how the stores allow free access to be given (offer or promotion codes, or access granted outside the store).
- **Stripe's card check.** From Stripe's own pages:
  - collecting a card at the start of a free trial and charging it when the trial ends;
  - the checks a card passes when it is saved (for example the security code and postal code), and what Stripe returns about it (for example the card's funding type, credit, debit or prepaid, its country, and a fingerprint that stays the same for the same card);
  - its fraud screening;
  - its prices;
  - what it keeps and for how long;
  - how a card's details stay out of Glow's own systems;
  - whether Stripe accepts a dating service. A05-V's record (section 10) found dating among Stripe's restricted businesses, and that record's facts are re-read here. The record says plainly whether Stripe's pages make a dating service prohibited, accepted only after Stripe's review, or accepted, and it names no other processor; if Stripe's pages exclude dating, the manager takes that to Nathan before the decision message.

**3. A facts table for the decision message,** each cell citing the rows and pages that bear on it, with no recommendation:
1. how the trial starts, converts and is cancelled in each channel (the App Store, Google Play, the Stripe link), and how long each lets it last;
2. what the card check shows for each of the three purposes, in each channel, and what it cannot show (for example whether a card is held only by adults);
3. what Glow keeps about the card and what the processor or store keeps;
4. what it costs: store commission and fees, external-link fees, and Stripe's fees;
5. what subscription law asks of the trial: disclosures, consent, reminders before a trial converts, and online cancellation;
6. how a staff grant of a free account works in each channel, and whether a granted account can pass the card check without being charged;
7. what a member can do when the card check fails.

## Owned paths (the session)

- `docs/planning/store-legal-safety-requirements.md`: the rechecked rows, their dates, any new rows, the Rows columns of sections 7 and 8 where a row is added, the header's Rechecks entry for this recheck, and each sentence of sections 9 and 10 that states a rechecked row whose requirement or status changed, corrected and marked as corrected at this recheck.
- `docs/testing/evidence/<the session's date>-a05-v2-card-check-and-paid-trial.md`: the session's record (method, sources with their hashes, the quotation checks, the three questions, the facts table, deviations and limits).

## Manager-owned

This brief; the prompt; the carried-items file; the handoff; the owner-direction register; the review log; PF01; the decision message.

## Exclusions

All code, configuration, workflows and other Markdown. No account, sign-up, trial, test-mode key, API call, form, sales contact or message to Stripe, a store or anyone else. No call to Stream, a database, HDE or Railway. No statement that Glow is, or would be, compliant (DM-37 1.1). No plan or price is proposed: those are Nathan's (A06).

## Dependencies and inputs

Public web pages only. The session reads OD-55, OD-60, OD-61, OD-68 and OD-69 in the owner-direction register; DM-84 sections 4 and 5; the A05-V record (`docs/testing/evidence/2026-11-17-a05-v-verification-services.md`), sections 1, 7.2, 10 and 11 and appendix C.2 (Stripe's restricted-business list), for its method and its Stripe facts; PF01's §7 "Billing" and its A06 row; and the matrix's sections 1, 8, 9 and 10.

## Acceptance checks

- `git diff --name-only <START_SHA> HEAD` prints only the two owned paths.
- Every row ID present at `<START_SHA>` is present at the head, in the same order (A05-V's script).
- Every rechecked row's Source cell carries `rechecked <today> (A05-V2)`, or the record names it as not re-read, with the reason.
- Each rechecked row's quotation is found as one continuous string in the stripped text of the source read today; the record's table lists each row, its source's SHA-256 and the result.
- Each fact for the three questions names its page and the date read; each new row names its primary text and the rows it was compared with.

## Classification expectation

`ordinary-docs-only`: both owned paths are Markdown, outside any `.claude/` directory.

## Evidence home

The session's record; the manager's verification is added to it as a section.

## Report format

Branch, start and head SHAs, changed paths, the rows rechecked (with any changed requirement named), the rows added, the three questions' findings in short, the sources unread with their URLs, every acceptance check with its exact result, deviations and open questions.

## Review plan

The change is Markdown only, so no code review applies. The manager verifies: the ID script; a sample of the quotation checks re-run from fresh fetches; every changed requirement and every new row read against its source; each corrected sentence of sections 9 and 10 read against its row. The decision message built from the record goes to the Dev Manager before Nathan.

## Sessions

None yet.
