# The A05 founding-member offer decision message — who can buy it, where it is sold, what "lifetime" means, a trial first, and the count and refunds

- **Owner:** App Manager 12. For Nathan, after Dev Manager 5 reads it (DM-89; OD-32).
- **Revision 2, 18 November 2026,** with DM-89's VV1 to VV12 applied as given (Dev Manager 5, `292c7ba`, a read of `f61f65a`). Revision 1 was the text DM-89 read.
- **Why:** OD-70 adds a founding-member offer: up to 1,000 members, a lifetime subscription for $100 paid once (the manager's reading of "a one-time thing"), ideally only through Stripe. A05-V3's research shows what the laws and the stores say about it ([its record](../testing/evidence/2026-11-18-a05-v3-founding-member-offer.md), sections 7 to 13; the manager's checks, section 17). DM-87 section 5 and DM-88 section 6 set the points this message puts to him. Row IDs below are the [requirements matrix](../planning/store-legal-safety-requirements.md)'s.
- **Where the answer goes:** a new OD row; the carried-items file's P08.3 entry; the Work Register's A05 and A06 rows.
- **Deletion condition:** prune after Nathan's answer is in the register and the Dev Manager's next consultation has read this message as sent.

---

**Five decisions on the founding-member offer.** Nothing breaks today: there are no members, and the offer comes after launch. The billing item's brief needs these answers to design its checkout and its terms.

| # | Question | Recommendation |
|---|---|---|
| F1 | Who can buy it? | **US buyers only: said in the offer's terms, and enforced with a Stripe rule that refuses non-US cards** |
| F2 | Where is it sold, and can the apps honour it? | **Through Stripe, as you prefer, adding a store's own purchase only if the billing item finds that store requires it** |
| F3 | What does "lifetime" mean? | **For as long as Glow runs the service, said plainly; and legal advice on the offer's form before it is sold** |
| F4 | Can a member buy it during a free trial? | **Yes, at any time, with the store's cancel step shown where Glow cannot stop the trial's charge** |
| F5 | How are the 1,000 counted, and what refunds apply? | **The first 1,000 paid, a refunded place reopening; refunds as the laws require, stated in the terms** |

**What this message is and is not.** The law, store and Stripe facts are A05-V3's, read from primary sources on 18 November 2026, for the US only (OD-55); the manager re-read 25 of its quotations. It is not legal advice, and it does not show that Glow is or would be compliant: where a text's effect on a plan with no end date is unclear, the record leaves it unresolved, and so does this message. The recommendations weigh what one operator can run (OD-23) and how plainly a buyer is told what they get. They do not weigh your business reasons, and those can outweigh them. Nothing here spends money now: a Stripe account is a line of the costed list (M07; OD-50). Two recommendations would add costs: F1's Stripe rule, and F3's legal advice, which has no price yet and would be a new line you approve first (OD-50).

## F1 — Who can buy it

- **What it is:** the launch is the US, all states, for now (OD-55). Through Stripe, Glow sells the offer itself, and a web checkout can be reached from abroad.
- **What breaks without it:** the brief cannot set the checkout's limits or the terms' scope.
- **The facts:**
  - If the offer were sold to buyers in the UK or the EU, the rows there that bind a paid contract would bear on it, among them 14 days to cancel (UK-46, EU-57). A05-V3 did not read them.
  - Stripe's Checkout and Payment Links can limit only the countries offered for a shipping address; no setting found limits the billing country or the card's country.
  - Stripe's fraud rules can test the card's issuing country and the buyer's IP country. Custom rules need Radar Plus or Pro, at $0.07 or $0.09 per screened payment; since Radar *"screens all payment attempt types"*, the fee would apply to the plan's payments too, not only the offer's (a reading of Stripe's pages). Stripe's own example rule refusing non-US cards carries its comment *"This rule is too broad and blocks a high number of legitimate payments."*
  - No control read establishes where a buyer lives: each tests one attribute (address, card country, IP location).
- **Options:**
  - **(a)** US only, said in the terms and enforced with a rule that refuses non-US cards (Radar Plus).
  - **(b)** US only, said in the terms, with no technical block.
  - **(c)** open to buyers anywhere.
- **What each gains:** (a) keeps the sale where the research was done; it also refuses a US resident paying with a foreign card. (b) costs nothing extra, but a non-US buyer can still pay. (c) reaches more buyers, but brings in the UK and EU rules, which are not researched.
- **Recommendation: (a).**

## F2 — Where it is sold, and whether the apps can honour it

- **What it is:** you would ideally sell the offer only through Stripe. Under C3 (OD-70), the Stripe link shows in the iPhone app and on the web, not in the Android app.
- **What breaks without it:** the brief cannot say where the offer is bought, or how a founding member gets the plan in each app.
- **The facts:**
  - **Stripe:** a one-time payment through Checkout or a Payment Link; $3.20 on $100 with a domestic card. Online dating is a business Stripe accepts only after its own review (A05-V2).
  - **The iPhone app:** on the US storefront, links to other purchase methods are allowed (AP-42). But 3.1.3(b) lets an app give access to what a user *"acquired in your app on other platforms or your web site"* only *"provided those items are also available as in-app purchases within the app"*. Whether that proviso applies on the US storefront is not stated on Apple's page.
  - **An in-app lifetime plan on the iPhone:** a "Non-Consumable" (*"does not expire"*) or a "Non-Renewing Subscription" (*"a limited duration"*). No Apple page says which a plan with no end date is. Apple keeps 30% ($30 on $100), or 15% ($15) in its Small Business Program.
  - **The Android app:** Google allows a "consumption-only" app to give access to *"content paid for somewhere else"*, but consumption-only means nothing can be bought in the app, and Glow's Android app sells the plan through Play. Its FAQ also says *"We do not require parity across platforms."* No Google page read addresses this case. A one-time item through Play's billing costs 15% ($15 on $100) on the first US$1M.
- **Options:**
  - **(a)** Stripe only, on the web and through the iPhone app's link. If a store's rules bar its app from honouring a plan bought outside it, founding members on that app cannot use the plan there.
  - **(b)** Stripe, plus each store's own one-time purchase at $100 in its app, so every member can buy and use it where they are; the stores keep 15% to 30% of those sales.
  - **(c)** Stripe now, and a store's own purchase added only if the billing item's brief finds that store requires it.
- **What each gains:** (a) keeps every sale at Stripe's fee, at the risk that an app cannot honour it. (b) works in both apps whatever the stores' rules turn out to be, at the stores' commission. (c) keeps your preference and adds a store's cost only where a rule requires it; the risk is that the answer comes late, at a store's review.
- **Recommendation: (c).**

## F3 — What "lifetime" means, and legal advice

- **What it is:** what the buyer is promised when the offer says "lifetime".
- **What breaks without it:** the brief cannot write the offer's terms.
- **The facts:**
  - **Contracts measured by a life:** five state dating-service laws bar a term *"measured by the life of the buyer"* or *"customer"*, or extending *"for the life of the customer"*: California, Colorado, Illinois, Arizona and Ohio (UST-22, UST-28, UST-26, UST-27, UST-62).
    - California and Colorado do not apply that paragraph to an online contract whose initial and later terms are each a year or less.
    - Illinois, Arizona and Ohio state no online exception.
    - Where these laws apply, a contract that does not comply with them is void in California, Colorado, Illinois and Arizona (UST-23, UST-28, UST-26, UST-27), and a California buyer may cancel it at any time (UST-22).
  - **Term and payment limits:** the shortest is Arizona's initial term of no more than one year, with an option to renew for a year (UST-27); Illinois allows an initial term of up to two years, with renewals of a year or less (UST-26), and Minnesota a term of up to 18 months (UST-64). Payments may run no more than two years (California, Colorado) or three (Illinois, Arizona), and services no more than three years (California, Colorado, Ohio, North Carolina). New York caps the cash price at $1,000 and the services at two years, with an online exception for terms of a year or less where a higher payment is reasonable; its Bill of Rights states no exception (UST-24).
  - **Whether any of these reach a single payment for an online plan with no end date is not stated in the texts.** That is a reading for counsel.
  - **Refunds on death or disability:** they are measured by services not yet received (California, Colorado), by the time before death (Illinois, for death only), prorated (Ohio), or at least 90% of the pro rata cost of unused services (North Carolina). No text says how that is measured for a lifetime.
  - **"Lifetime" claims:** the FTC's guide (USF-23) and Colorado's rule (UST-67) say a "lifetime" claim should disclose whose life it means. Both are written for warranties and guarantees, and whether they reach a plan is not stated.
  - **Stripe:** it may apply remedies, among them a reserve, to payments for services *"not immediately deliverable"* taken without its consent. For a future service, a card dispute's window starts on the event date. How either applies to access with no end date is not stated.
- **Options:**
  - **(a)** "Lifetime" means for as long as Glow runs the service, said plainly at purchase; and take legal advice on the offer's form before it is sold.
  - **(b)** The same meaning, without legal advice.
  - **(c)** A fixed term instead of "lifetime", such as a set number of years. The term limits above bear on a long fixed term too.
- **What each gains:** (a) tells the buyer what they get, and puts the five life-measure bars and the term limits to someone who can read them, at a cost not yet priced. (b) is faster and costs nothing now, but leaves those questions open at sale. (c) avoids the word "lifetime", but not the term limits.
- **Recommendation: (a).** Whether to take legal advice stays yours (DM-31); this offer is where the research found the most questions it cannot settle.

## F4 — A member already in a free trial

- **What it is:** whether a member can buy the offer during OD-69's two-week trial, and how the trial's charge is stopped.
- **What breaks without it:** the brief cannot design the move from the trial to the offer.
- **The facts:**
  - A member in the trial is under the trial's own rules until it ends or is cancelled (UST-29, UST-30, UST-60).
  - **A Stripe trial:** Glow ends it with no charge.
  - **A Google trial:** Glow can defer its billing, from one day to one year at a time (A05-V2). No page read says Glow can end it; the member can cancel it in Play.
  - **An App Store trial:** only the member can stop the charge, by cancelling in Settings; otherwise Apple charges when the trial ends (OD-70, C5).
  - So a member in an App Store trial who buys the offer through Stripe is charged by Apple unless they cancel themselves.
- **Options:**
  - **(a)** any member may buy it, during a trial or after, with the store's cancel step shown to members in an App Store trial, and to members in a Google Play trial unless the billing item finds that Glow can end it;
  - **(b)** only at signup, in place of the trial;
  - **(c)** only after the trial ends or is cancelled.
- **What each gains:** (a) is open to everyone, but a member in an App Store trial, and perhaps one in a Google Play trial, must take one step to avoid a charge. (b) avoids any overlap, but shuts out members already in a trial. (c) avoids a double charge, but makes a member wait or cancel first.
- **Recommendation: (a).**

## F5 — How the 1,000 are counted, and refunds

- **What it is:** what fills a place, and what a founding member can get back.
- **What breaks without it:** the brief cannot set the counter or the refund terms.
- **The facts:**
  - **No law or store page read uses "founding" or sets a rule on a limited number of buyers.** Illinois and Arizona bar misrepresenting the number of other members (815 ILCS 615/40(a); §44-7154(D)(3)).
  - **Cancellation windows** apply whatever Glow adds: three business days in most of the states read, and seven days in Illinois for a purchase not made at a facility. Refunds are due within 10 days to 30 days.
  - **Stripe:** no time limit on refunding a card payment was found, and its original fees are not returned on a refund. A dispute costs $15. Cardholders usually have 120 days, and for a future service the window starts on the event date.
- **Options:**
  - **Count:** **(a)** the first 1,000 paid, a refunded place reopening; **(b)** the first 1,000 paid, refunds not reopening a place.
  - **Refunds:** **(i)** the laws' refunds only, stated in the terms; **(ii)** also a money-back period of your choosing.
- **What each gains:**
  - (a) keeps the offer at 1,000 members; (b) is simpler, but can end with fewer than 1,000.
  - (i) is what every buyer gets by law; (ii) may head off disputes, at the cost of refunds Glow need not give.
- **Recommendation: (a) and (i).**

## Not decisions now

- **Stripe must approve Glow first.** Only Stripe's review, after an account is opened, can say whether it accepts a dating service. Opening one waits for your approval of its line (M07). Until then, neither the trial's Stripe link nor this offer can run.
- **The price and the cap stand as you set them:** $100, and 1,000 members (OD-70).
- **When the offer closes if fewer than 1,000 buy** is yours to set before it opens: you said it is *"for the initial post launch"* (OD-70), and its terms will need the date.
