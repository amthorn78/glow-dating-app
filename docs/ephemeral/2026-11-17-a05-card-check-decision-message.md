# The A05 card-check decision message — what the card is for, where it is checked, the trial's length and staff grants

- **Owner:** App Manager 12. For Nathan, after Dev Manager 5 reads it (DM-86; OD-32).
- **Revision 2, 17 November 2026,** with DM-86's SS1 to SS14 applied as given (Dev Manager 5, `5a53db6`, a read of `4d4693d`), and one sentence of the manager's in C3 made to agree with SS10 (option (b)'s fee), for the Dev Manager's read of the message as sent. Revision 1 was the text DM-86 read.
- **Why:** OD-68 and OD-69 set a paid plan with a free trial at signup, a card given then, and a card check for three purposes. A05-V2's research shows what a card check can do in each place a member can subscribe ([its record](../testing/evidence/2026-11-17-a05-v2-card-check-and-paid-trial.md), section 10; the manager's checks, section 14). DM-85 section 7 adds two questions on staff grants. PF01 §7 "Billing" holds purchase screens off until the billing item's brief, which needs these answers. Row IDs below are the [requirements matrix](../planning/store-legal-safety-requirements.md)'s.
- **Sent** to Nathan in the manager session on 17 November 2026, as revision 2, as written below. **Answered** the same evening: *"Accepted."*, with a founding-member offer added (OD-70).
- **Where the answer goes:** a new OD row; the carried-items file's P07 and P08.3 entries; the Work Register's A05 and A06 rows. PF01 does not change: its A06 row already leaves the trial's length to Nathan, and PF01 changes only when a rule does (DM-01 P3).
- **Deletion condition:** prune after Nathan's answer is in the register and the Dev Manager's next consultation has read this message as sent.

---

**Five decisions on the card check and the free trial.** Nothing breaks today: there are no members, and purchase screens stay off until the billing item's brief. That brief needs these answers.

| # | Question | Recommendation |
|---|---|---|
| C1 | What can Glow rely on the card for? | **A payment method, and one free trial for each store account or card. Not proof of age: the age check stays as OD-55 set it** |
| C2 | Where is the card checked for a member who subscribes in the app? | **By the store's own billing. Stripe's check runs only for a purchase through the Stripe link** |
| C3 | Does the Android app carry the Stripe link? | **No: the iPhone app and the web only** |
| C4 | How long is the free trial? | **Two weeks** |
| C5 | How do staff grants of a free account work? | **Staff may grant one without a card; a grant during a trial stops the charge wherever Glow can** |

**What this message is and is not.** The store, Stripe and law facts are A05-V2's, read from primary sources on 17 November 2026, for the US only (OD-55); the manager re-read the ones the recommendations rest on. It is not legal advice, and it does not show that Glow is or would be compliant. The recommendations weigh what one operator can run (OD-23) and how little card data Glow holds. They do not weigh your pricing or business reasons, and those can outweigh them. Nothing here spends money: a Stripe account and the store accounts are lines of the costed list, each for your approval (M07; OD-50).

## C1 — What the card can be relied on for

- **What it is:** you set three purposes for the card (OD-69): a payment method ready for the trial's end; fake or duplicate accounts made harder; and showing that the member is an adult.
- **What breaks without it:** the billing item's brief cannot say what a passed card check records, or what the age check rests on.
- **The facts:**
  - **A payment method.** In the apps, the store holds it, and the fields it sends Glow carry no card details (A05-V2's reading of their field lists; neither store says it in so many words). Google Play checks for a valid payment method before a free trial starts; no Apple page read says Apple does for an app's trial (unconfirmed). Through the Stripe link, Stripe saves the card when the trial starts and charges it when the trial ends. When Stripe checks the card, which it does not always do (*"automatic verification isn’t always performed"*), the check confirms only that the card is valid: it *"cannot check credit limits or account balances"*, and the security-code and postal-code checks are sometimes skipped.
  - **One free trial each.** In the apps, Glow sees no card at all: Apple says *"each person is only eligible to redeem one introductory offer per subscription group"*, and Google has an *"Allow one free trial per app"* setting. Through the Stripe link, Stripe returns a fingerprint that is the same for the same card number, and the card's type (credit, debit or prepaid) and country. So the limit is the store account's or the card's: neither store says how it tells that two accounts are one person (Google says only that Play *"may detect"* attempts to get round it), and through the link a second card starts a second trial. Stripe's fraud screening *"doesn’t act on the SetupIntent by default"* when a card is saved for a trial; blocking free-trial abuse needs Radar Pro, a paid tier.
  - **Adulthood.** No source read shows that a card is held only by adults, or that the person using it is its holder. Stripe reports debit and prepaid cards among card types, and its card record has no age or birth-date field. No age row of the matrix names a card check run by an app as an age check (AP-14; UST-32 to UST-41), though New York's rule text under UST-38 was not read. Apple's age-range interface can answer that a person's age range *"has been confirmed using a credit card or government ID"* (AP-14). That is Apple's check, which Glow would read through Apple's interface, not a card check of Glow's.
- **Options:**
  - **(a)** rely on the card for the payment method and the one-trial limit only. The age check stays as OD-55 set it: the member's own birth date, plus the stores' age signals where the law requires them, behind the seam that lets a stronger check be added.
  - **(b)** also count a passed card check as a sign of adulthood in the member's age state.
- **What each gains:** (a) claims only what the card shows. (b) adds a sign that a minor's debit card, a parent's card or a prepaid card would also pass, and if it is recorded as an age check, it claims what no source supports.
- **Recommendation: (a).**

## C2 — Where the card is checked for a member who subscribes in the app

- **What it is:** in the apps, Apple and Google take the payment, and the fields they send Glow carry no card details. A card check of Glow's own would mean the member also gives a card to Stripe.
- **What breaks without it:** the brief cannot design the signup screens.
- **The facts:**
  - No page of either store read addresses a card check outside its billing that only verifies. The nearest rules: Apple bars an app's *"own mechanisms to unlock content or functionality"* (3.1.1) and asks an app to collect only the data its task needs (5.1.1). Google's payments policy bars sign-up flows *"that lead users from an app to a payment method other than Google Play's billing system as part of those flows"*.
  - A member who subscribes in the app would give a card twice: to the store, and to Stripe.
- **Options:**
  - **(a)** each channel's own check. In the apps, the store's billing and its one-trial rules. Through the Stripe link, Stripe's check, with one free trial per card number; a member whose card fails may try another card, and no trial starts without one that passes.
  - **(b)** every member also gives a card to Stripe at signup, checked and never charged, whichever way they subscribe.
- **What each gains:** (a) stays within what the store pages say and asks for one card; in the apps, the duplicate check is only the stores' one-trial rules. (b) gives Glow a card fingerprint for every member, at the risk that a store rejects the app at review: no store text allows it, and the nearest texts point against it.
- **Recommendation: (a).** (b) can be weighed again if fake accounts become a problem, with the stores' current rules read first.

## C3 — The Stripe link in the Android app

- **What it is:** you chose a link to a purchase through Stripe beside the stores' billing (OD-69). On the US storefront, Apple allows the link, and the pages read state no Apple fee for it (AP-42). Google allows it only through its external content links programme (GP-39).
- **What breaks without it:** the brief cannot say which apps show the link.
- **The facts (US):**
  - **Google's programme:** enrolment first; Google's own information screen before the member leaves the app; every transaction reported, $0 trial purchases included; a fee of 10% on a subscription bought within 24 hours of following the link. Renewals are reported too, but the pages read do not say whether each renewal carries the 10%.
  - **Fees in the Android app:** through Play's billing, 15% (10% and a 5% billing fee). Through the link, Google's 10% plus Stripe's 2.9% + 30¢ and its billing fee of 0.7%: about the same as Play's 15% at a $20 price, more below it and a little less above it, if each renewal carries Google's 10%. If renewals do not, the link costs Stripe's fees alone after the first payment.
  - **Fees in the iPhone app:** Apple keeps 30% in a subscriber's first year and 15% after, or 15% throughout in its Small Business Program. Through the link, Stripe's fees; the pages read state no Apple fee.
- **Options:**
  - **(a)** the link in the iPhone app and on the web, and not in the Android app, where members subscribe through Play's billing.
  - **(b)** the link in both apps, with Google's programme.
- **What each gains:** (a) keeps the link where it saves the most, and leaves out Google's enrolment, its interface and the transaction reports. (b) offers one way to pay everywhere, for about Play's own fee if each renewal carries Google's 10%, and less if it does not. Whether the Android app may honour a plan bought through the link is for the brief to settle from Google's text. The nearest text read lets an app let a user *"access content paid for somewhere else"* only when nothing can be bought in the app, and the Android app sells the plan through Play. Under (a), every member who pays through the link meets that question on Android; under (b), the Android app's own link is a route Google's programme provides.
- **Recommendation: (a).**

## C4 — How long the free trial lasts

- **What it is:** how long a new member has before the plan is charged. The plan and its price stay yours to set when the brief needs them.
- **What breaks without it:** the brief cannot set up the trial, or know which reminder notices apply.
- **The facts:**
  - **Lengths:** Apple offers a fixed set: 3 days, 1 or 2 weeks, 1, 2, 3 or 6 months, or 1 year. Google allows 3 days to 3 years, and Stripe up to 730 days.
  - **Longer trials bring more notices:** Virginia asks for a notice of the option to cancel when a trial lasts more than 30 days (UST-60), and California for a notice 3 to 21 days before the end of a trial of more than 31 days (UST-29). A trial of any length still has the three states' other rules: the price after the trial shown before consent, how to cancel before paying, easy cancellation, and Colorado's notice 25 to 40 days before the first automatic renewal (UST-29 to UST-31).
  - **Reminders:** Google emails the member before a trial ends; Stripe can email a reminder 7 days before, or at the start of a shorter trial; no Apple page read says Apple sends one.
- **Options:** **(a)** 1 week; **(b)** 2 weeks; **(c)** 1 month; **(d)** another length from Apple's set.
- **What each gains:** (a) and (b) are under both states' thresholds in every channel; (b) gives a new member twice as long to find matches while the launch pool is small. (c) runs 31 days in some months, which passes Virginia's 30.
- **Recommendation: (b), 2 weeks.**

## C5 — Staff grants of a free account

- **What it is:** a free account comes only from a staff grant (OD-69). Two questions follow (DM-85): **(a)** may staff grant a free account to someone who has never given a card, such as an invited member? **(b)** Does a grant made during a member's trial stop the trial's charge?
- **What breaks without it:** P07's console and P08.3 cannot design the grant.
- **The facts:**
  - **No store or Stripe page read uses the idea of a staff grant.** Apple lets an app give access to a plan *"acquired in your app on other platforms or your web site"* only if the plan is also sold in the app (3.1.3(b)), and it bars an app's own unlocking mechanisms (3.1.1). How a grant reaches the iPhone app is for the brief to settle.
  - **Each channel's tools:** Apple's offer codes (free for a set time, up to 1 million redemptions a quarter; a free code can be set not to renew); Google's promo codes (a free trial of 3 to 90 days) and deferred billing (free access for an existing subscriber, up to a year at a time); Stripe, a subscription Glow controls, which can start without a card. No page read says whether redeeming an Apple free offer code, or starting a Google promo code's trial, needs a payment method, so a grant to someone with no card is sure only through Stripe until the brief settles it.
  - **Stopping a charge:** Glow controls a Stripe subscription, and Google lets the developer defer a subscriber's billing. For an App Store trial, the Apple pages read show no way for the developer to stop the charge: the member cancels in Settings, and Apple's renewal extensions apply only after a paid period.
- **Options for (a):** **(i)** yes: staff may grant a free account to someone with no card; it skips the card check, and the grant records who gave it and why. **(ii)** no: every member gives a card first, and grants come only after signup.
- **Options for (b):** **(i)** yes, wherever Glow can: a Stripe trial ends with no charge, and Glow keeps only the card's fingerprint for the one-trial check; a Google trial's billing is deferred; an App Store member is told to cancel in Settings before the trial ends, and the grant keeps their access. **(ii)** no: staff grant only to a member with no trial or plan running, so the member cancels first.
- **What each gains:** (a)(i) lets you invite people without asking for a card; a grant is a deliberate staff act for one named person, so the duplicate risk the card guards against is staff's to judge. (a)(ii) keeps every account behind the card check. (b)(i) spares a granted member a charge everywhere except the App Store, where only the member can stop it. (b)(ii) is simpler to build, but the member must act first.
- **Recommendation: (a)(i) and (b)(i).**

## Stripe's approval, and the law that follows

- **Not a decision now: Stripe must approve Glow first.** Stripe lists online dating among the businesses it accepts only after its own review, and its agreement asks for its written approval. Its adult-content exclusion names sexually oriented dating services, and its prohibited list includes *"Negative option marketing, negative option membership clubs, and reduced price trials with unclear or hidden pricing"*, so the trial's price and how to cancel must be plain. Only Stripe's review, after an account is opened, can say whether it accepts Glow, and opening one waits for your approval of its line (M07). If Stripe declines, the apps' billing still works, and the link and its card check wait.
- **Subscription law applies whatever you choose:** the trial's terms before the card is taken, consent, reminders and online cancellation (USF-16; UST-29 to UST-31, UST-60 and UST-61), and the dating-service contract laws for a paid service (UST-22 to UST-28). P08.3 owns them (gap G-07). Whether to take legal advice before the paid launch stays yours (DM-31).
