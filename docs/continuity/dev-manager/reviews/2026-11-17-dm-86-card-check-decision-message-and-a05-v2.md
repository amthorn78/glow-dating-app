# DM-86 — the card-check decision message, A05-V2's integration, PF01 1.18 and PF02 1.4

- **From:** Dev Manager 5 (`session_01Q789u3CWg6s9pBGXerCQZt`), for App Manager 12, relayed by Nathan (OD-25).
- **Date:** 17 November 2026. Received about 22:16 UTC; finished about 22:25 UTC.
- **Read at:** `4d4693dad6faa9d4ab2282e1f5b361087a490848` of `claude/magical-wozniak-yfmmx2`, exported outside any worktree.
  - `main` is at `a316a3a` (PR51's merge), the only merge base. No pull request is open.
  - The governing diff since my last read (`8d272a4`) is PF01 (RR4 to RR7, at `b9534a9`) and PF02 (revision 1.4, at `aae7f07`). `AGENTS.md`, `CLAUDE.md`, PF00, the manager workflow, my charter and the CI policy are unchanged.
- **Environment:** names only. None of `DATABASE_URL`, `HD_API_KEY`, `GEO_API_KEY`, or any `STREAM_*`, `PG*`, `R2_*`, `CLOUDFLARE_*`, `CF_*` or `RAILWAY_*` name is set. The AWS names are present and were not read.
- **What I changed:** this file only, on `claude/dev-manager`. Notion was read, not changed. No call to Stream, a database, HDE, Railway or Cloudflare, and no public web page was fetched.
  - I ran the trusted classifier from `a316a3a`, extracted outside the worktree, under `python3 -I`.

## 1. The answers

| Item | Verdict |
|---|---|
| 1. The decision message | **Approved with conditions: SS1 to SS14.** The five decisions are all his, and none he needs is missing. The facts are read rightly except in four places, each fixed in the message's own words: "one free trial per person" (SS2, SS5, SS7); Stripe's check, which does not always run (SS4); Google's 10% on renewals, which no page read settles (SS9, SS10); and the Android app honouring a plan bought through the link (SS11). A missing limit on adulthood and three omissions are restored (SS6; SS12 to SS14), and PF01 needs no change for the trial's length (SS1) (section 3) |
| 2. A05-V2's integration | **Accepted.** Every step of the brief's review plan is done, and done rightly (section 4) |
| 3. Section 1's counts | **Approved as you propose, in SS15 and SS16.** By my script: 333 rows; 84 with no owner; 88 not applicable now (section 5) |
| 4. PF01's revision 1.18 | **Confirmed.** PF01 at the head is revision 1.17 with RR4 to RR7, exactly (section 6) |
| 5. PF02's revision 1.4 | **Approved as written.** Coverage 187 of 187 (section 7) |
| 6. The sequence | **Agreed** (section 8) |
| 7. Notion | **Matches,** except A06's Work Register row (section 9) |

## 2. What I read and checked

- **The classification.** The trusted `scripts/change_scope.py` from `a316a3a`, run with the full SHAs of `a316a3a` and `4d4693d` and `--merge-base`, gives `ordinary-docs-only` on 12 paths, with one merge base. No path is outside Markdown or under `.claude/`.
- **DM-85's words:**
  - a script found each of RR1 to RR18's new texts and none of their old passages;
  - rebuilding the register, PF01 and the carried-items file from `8d272a4` with RR1 to RR18 applied gives the head. The only difference is the register's line on OD-69's other option, which I asked you to write.
- **PF02's revision 1.4:** the diff from `8d272a4`, AM12-16 in the log, and the coverage, by script.
- **The decision message, whole,** against A05-V2's record:
  - its sections 6 to 8 (the three questions), 10 (the facts table), 13 (the limits and open questions) and 14 (your verification);
  - each quotation the message uses, found in the record's text by script;
  - the matrix's UST-29 to UST-31, UST-38, UST-60, UST-61 and GP-17, whole.
- **The integration:** the matrix at `b9534a9`, at `e23829b` and at the head, by script. I checked the 43 rows' recheck marks, the rows changed outside them, the rows added, their order, and section 1's counts.
- **Notion:** section 9.
- **No error of my own** was found in this round.

## 3. Item 1 — the decision message

**Whose decisions: all five are his.**
- **C1** is about the purposes he set for the card (OD-69).
- **C2** decides how his "At signup the member gives a card" is met for a member who subscribes in an app.
- **C3** narrows his own direction, "a link to purchase outside it (via stripe)". So it is **his to decide, not the billing item's.** The billing item builds what he chooses.
- **C4** is the trial's length, which PF01's A06 row leaves to him.
- **C5** holds DM-85's two staff questions.

**No decision he needs is missing.**
- **A failed card check:** C2's option (a) gives the rule ("no trial starts without one that passes"). What counts as passing is for the billing item's brief, since a check can also come back `unavailable` or `unchecked`. It is not a question for him.
- **Stripe's approval:** rightly stated as a risk, not a decision. The decision it leads to is the costed-list line for a Stripe account (OD-50), which comes with the billing item. The message says so.

**The facts: four readings to correct.**
- **"One free trial per person" (SS2, SS5, SS7).**
  - Apple's words are "each person". Google's setting is per app, for a user's account. Stripe's fingerprint identifies a card number.
  - No page read says how a store tells that two accounts are one person; Google says only that Play "may detect" attempts.
  - So the card limits one trial per store account or per card, not per person. Through the link, a second card starts a second trial.
  - Stripe's fraud screening "doesn't act on the SetupIntent by default", and blocking free-trial abuse needs Radar Pro, a paid tier. C1's second purpose rests on these facts, so the message states them.
- **What Stripe's check confirms (SS4).** The message says the check "confirms the card is valid". The record says Stripe's automatic verification "isn't always performed", and that when it runs it confirms only validity.
- **Google's 10% on renewals (SS9, SS10).**
  - The programme's fee text covers transactions "within 24 hours of following an external content link". Renewals are reported, but no page read says whether each renewal carries the 10%.
  - C3's comparison ("about the same as Play's 15%") holds for every payment only if renewals carry the fee. If they do not, the link costs Stripe's fees alone after the first payment. Whichever way, he should see that the comparison rests on it.
- **The Android app honouring a plan bought through the link (SS11).**
  - The message says this is "for the brief to settle ... under either option". The two options are not alike.
  - The nearest text read lets an app give access to "content paid for somewhere else" only when nothing can be bought in the app, and the Android app sells the plan through Play.
  - Under (a), every member who pays through the link meets that question on Android. Under (b), the Android app's own link is a route Google's programme provides.
  - This may change how he weighs C3, so he should see it. Whether your recommendation still stands with it is yours to judge; the words only state the fact.

**Two readings you asked about are right:**
- **C1, adulthood.** The record finds no source showing a card is held only by adults, and no age row naming an app's card check as an age check. One limit is missing: New York's rule text under UST-38 was not read (SS6).
- **C5, the App Store.** The pages read show no way for a developer to stop an App Store trial's charge. The member cancels in Settings, and renewal extensions need "at least one previously paid period". "Where only the member can stop it" is a fair summary of that.

**Three omissions to restore:**
- **C4 (SS12):** the "rules for a trial of any length" leave out Colorado's notice 25 to 40 days before the first automatic renewal (UST-30), which the facts table lists.
- **C5 (SS13):** no page read says whether redeeming an Apple free offer code, or starting a Google promo code's trial, needs a payment method. So a grant to someone with no card is certain only through Stripe until the brief settles it, and his answer to C5 (a) should be made knowing that.
- **Stripe's approval (SS14):** Stripe's prohibited list includes "Negative option marketing, negative option membership clubs, and reduced price trials with unclear or hidden pricing". That bears on how the trial is shown, and on Stripe's review.

**The other changes:**
- **SS3 and SS8:** "Glow sees no card details" becomes what the record found: the fields the stores send carry none (a reading of their field lists; neither store says it in so many words).
- **SS1: PF01 does not change for the trial's length.**
  - Its A06 row already says no trial length is set except by Nathan, and that stays true once he sets one.
  - PF01 changes only when a rule does (DM-01 P3).
  - The message's "Where the answer goes" drops PF01, so his answer brings no governing change.

## 4. Item 2 — A05-V2's integration

**Accepted.** The brief's review plan, step by step:
- **The ID script:** run by you, and by my own script. 331 rows before and 333 after; none missing; none reordered; UST-60 and UST-61 added.
  - Each of the 43 rows carries "rechecked 2026-11-17 (A05-V2)", and no row outside them changed.
- **A sample of the quotation checks, from fresh fetches:** 15 quotations from 9 sources, then 15 from 11 sources for the facts the message rests on, all exact. Seven pages' hashes differ from the session's (dynamic pages, Virginia's dated by the day), and each quotation was found in the text read.
- **Every changed requirement and every new row, read against its source:** GP-17's new text, and UST-60 and UST-61 against Va. Code §59.1-207.46 (D) and (E).
- **Each corrected sentence of sections 9 and 10:** none was corrected, rightly. No sentence states GP-17, and the retention sentence on UST-29 still holds (the record's section 5.1).
- **The decision message to me before Nathan:** this consultation.
- **RR15:** Stripe's pages make a dating service "restricted", accepted after its review and written pre-approval, and do not exclude it. Not returning to Nathan first was right.
- **The open questions** (the record's section 13) are carried into the message, and SS13 adds the last one in full.

## 5. Item 3 — the matrix's section 1

- **Approved as you propose.** The words are SS15 and SS16.
- **By my script, at the head** (identical to the matrix at `e23829b`):
  - 333 rows: Apple 69, Google Play 65, US federal 22, US states 61, UK 50, EU 66;
  - 84 with no owner;
  - 88 whose State begins "Not applicable".

## 6. Item 4 — PF01's revision 1.18

- **Confirmed.** Rebuilding PF01 from `8d272a4` with RR4 to RR7 applied gives the head exactly: the header, §7's "Billing" sentence, A06's row and the 1.18 history line.
- It merged with PR51 at `a316a3a`. DM-85's deferred row for it can close.

## 7. Item 5 — PF02's revision 1.4

- **The texts:** AM12-16 is in section 7; section 8's bullet and section 9's 1.4 line record it; the header reads 1.4.
- **The placement:** the tool refused both empty calls before any write, with no effect. That is the log's rule for section 7, as for AM12-12 and AM12-13.
- **Coverage, by script:** the log holds 187 IDs, AM2-01 to AM12-16. Each appears in PF02, and PF02 names none outside the log.
- **Approved as written.**

## 8. Item 6 — the sequence

**Agreed.** Notes:
- **Step 2:** the message goes to Nathan with SS1 to SS14 applied. They are my words only, so it needs no further read from me. His answers go into a new OD row, which my next consultation reads.
- **Step 3, PR52:**
  - its governing Markdown is PF02's 1.4, read here;
  - SS15 and SS16 are a records correction in my words;
  - it merges after the run and Codex's summary on its final head and after its checklist.
- **Step 4:** the bounded change lands before P10, its brief comes to me first, and SV4 follows. Each is named to Nathan before it starts (OD-29).

## 9. Item 7 — Notion (read-only, at about 22:20 UTC)

| Page | What I compared | Result |
|---|---|---|
| Implementation Control, status | Last matched at `4d4693d`: A05-V2 verified, the decision message at DM-86 | **Match** |
| Its Branches bullet | Four branches, against `git ls-remote` now: `main` `a316a3a`, the manager branch `4d4693d`, `claude/dev-manager` `05c469d`, `claude/a05-v2-glow-card-check-1ucpsx` `e23829b` | **Match** |
| Its Main bullet | `a316a3a`, PR51's merge | **Match** |
| Its Mistakes log bullet | AM12-01 to AM12-16 at `aae7f07`, where the log last changed | **Match** |
| Its procedure summary | The stamp at `aae7f07`, where PF02 last changed, after PF01's change at `b9534a9` | **Match** |
| Dev Manager page, `DM-85` and `DM-86` | DM-85 considered (merge `2fd068c`); DM-86 awaited; six cells each | **Match** |
| The register copy | Matched at `495d55b`; 69 rows, as the repository; OD-69 equal in text, with its other option | **Match.** Seven older rows differ only in link text |
| Work Register, `A05`, `G-01`, `A05-V` and `A05-V2` | A05 names OD-69 and DM-86; G-01 names OD-68 and OD-69; A05-V done; A05-V2 verified | **Match** (DM-85's two rows corrected) |
| Work Register, `A06` | Ends "PF01's A06 row and §7 "Billing" wait for the Dev Manager (DM-85)" | **Mismatch, small.** PF01's revision 1.18 has made both changes, merged with PR51 at `a316a3a` |

## 10. The words

**SS1 — the decision message, `docs/ephemeral/2026-11-17-a05-card-check-decision-message.md` (yours): where the answer goes.**

> ```
> a new OD row; PF01's A06 row, for the trial's length; the carried-items file's P07 and P08.3 entries; the Work Register's A05 and A06 rows.
> ```

> ```
> a new OD row; the carried-items file's P07 and P08.3 entries; the Work Register's A05 and A06 rows. PF01 does not change: its A06 row already leaves the trial's length to Nathan, and PF01 changes only when a rule does (DM-01 P3).
> ```

**SS2 — the decision message, `docs/ephemeral/2026-11-17-a05-card-check-decision-message.md` (yours): C1 in the table.**

> ```
> **A payment method, and one free trial per person. Not proof of age: the age check stays as OD-55 set it**
> ```

> ```
> **A payment method, and one free trial for each store account or card. Not proof of age: the age check stays as OD-55 set it**
> ```

**SS3 — the decision message, `docs/ephemeral/2026-11-17-a05-card-check-decision-message.md` (yours): C1, the payment method in the apps.**

> ```
> - **A payment method.** In the apps, the store holds it and Glow sees no card details.
> ```

> ```
> - **A payment method.** In the apps, the store holds it, and the fields it sends Glow carry no card details (A05-V2's reading of their field lists; neither store says it in so many words).
> ```

**SS4 — the decision message, `docs/ephemeral/2026-11-17-a05-card-check-decision-message.md` (yours): C1, what Stripe's check confirms.**

> ```
> Its check confirms the card is valid; it *"cannot check credit limits or account balances"*, and the security-code and postal-code checks are sometimes skipped.
> ```

> ```
> When Stripe checks the card, which it does not always do (*"automatic verification isn’t always performed"*), the check confirms only that the card is valid: it *"cannot check credit limits or account balances"*, and the security-code and postal-code checks are sometimes skipped.
> ```

**SS5 — the decision message, `docs/ephemeral/2026-11-17-a05-card-check-decision-message.md` (yours): C1, one free trial.**

> ```
> - **One free trial per person.** In the apps, Glow sees no card at all; Apple allows one introductory offer per person, and Google has a one-trial-per-app setting. Through the Stripe link, Stripe returns a fingerprint that is the same for the same card number, and the card's type (credit, debit or prepaid) and country.
> ```

> ```
> - **One free trial each.** In the apps, Glow sees no card at all: Apple says *"each person is only eligible to redeem one introductory offer per subscription group"*, and Google has an *"Allow one free trial per app"* setting. Through the Stripe link, Stripe returns a fingerprint that is the same for the same card number, and the card's type (credit, debit or prepaid) and country. So the limit is the store account's or the card's: neither store says how it tells that two accounts are one person (Google says only that Play *"may detect"* attempts to get round it), and through the link a second card starts a second trial. Stripe's fraud screening *"doesn’t act on the SetupIntent by default"* when a card is saved for a trial; blocking free-trial abuse needs Radar Pro, a paid tier.
> ```

**SS6 — the decision message, `docs/ephemeral/2026-11-17-a05-card-check-decision-message.md` (yours): C1, adulthood.**

> ```
> No age row of the matrix names a card check run by an app as an age check (AP-14; UST-32 to UST-41).
> ```

> ```
> No age row of the matrix names a card check run by an app as an age check (AP-14; UST-32 to UST-41), though New York's rule text under UST-38 was not read.
> ```

**SS7 — the decision message, `docs/ephemeral/2026-11-17-a05-card-check-decision-message.md` (yours): C1, option (a).**

> ```
> rely on the card for the payment method and one trial per person only.
> ```

> ```
> rely on the card for the payment method and the one-trial limit only.
> ```

**SS8 — the decision message, `docs/ephemeral/2026-11-17-a05-card-check-decision-message.md` (yours): C2, what it is.**

> ```
> - **What it is:** in the apps, Apple and Google take the payment and give Glow no card details.
> ```

> ```
> - **What it is:** in the apps, Apple and Google take the payment, and the fields they send Glow carry no card details.
> ```

**SS9 — the decision message, `docs/ephemeral/2026-11-17-a05-card-check-decision-message.md` (yours): C3, Google's fee and renewals.**

> ```
> a fee of 10% on a subscription bought within 24 hours of following the link.
> ```

> ```
> a fee of 10% on a subscription bought within 24 hours of following the link. Renewals are reported too, but the pages read do not say whether each renewal carries the 10%.
> ```

**SS10 — the decision message, `docs/ephemeral/2026-11-17-a05-card-check-decision-message.md` (yours): C3, the fee comparison.**

> ```
> about the same as Play's 15% at a $20 price, more below it and a little less above it.
> ```

> ```
> about the same as Play's 15% at a $20 price, more below it and a little less above it, if each renewal carries Google's 10%. If renewals do not, the link costs Stripe's fees alone after the first payment.
> ```

**SS11 — the decision message, `docs/ephemeral/2026-11-17-a05-card-check-decision-message.md` (yours): C3, honouring a plan bought through the link.**

> ```
> Whether the Android app may honour a plan bought on the web is for the brief to settle from Google's text, under either option.
> ```

> ```
> Whether the Android app may honour a plan bought through the link is for the brief to settle from Google's text. The nearest text read lets an app let a user *"access content paid for somewhere else"* only when nothing can be bought in the app, and the Android app sells the plan through Play. Under (a), every member who pays through the link meets that question on Android; under (b), the Android app's own link is a route Google's programme provides.
> ```

**SS12 — the decision message, `docs/ephemeral/2026-11-17-a05-card-check-decision-message.md` (yours): C4, the rules for a trial of any length.**

> ```
> the price after the trial shown before consent, how to cancel before paying, and easy cancellation (UST-29 to UST-31).
> ```

> ```
> the price after the trial shown before consent, how to cancel before paying, easy cancellation, and Colorado's notice 25 to 40 days before the first automatic renewal (UST-29 to UST-31).
> ```

**SS13 — the decision message, `docs/ephemeral/2026-11-17-a05-card-check-decision-message.md` (yours): C5, a grant with no card.**

> ```
> Stripe, a subscription Glow controls, which can start without a card.
> ```

> ```
> Stripe, a subscription Glow controls, which can start without a card. No page read says whether redeeming an Apple free offer code, or starting a Google promo code's trial, needs a payment method, so a grant to someone with no card is sure only through Stripe until the brief settles it.
> ```

**SS14 — the decision message, `docs/ephemeral/2026-11-17-a05-card-check-decision-message.md` (yours): Stripe's approval, the trial's pricing.**

> ```
> Its adult-content exclusion names sexually oriented dating services.
> ```

> ```
> Its adult-content exclusion names sexually oriented dating services, and its prohibited list includes *"Negative option marketing, negative option membership clubs, and reduced price trials with unclear or hidden pricing"*, so the trial's price and how to cancel must be plain.
> ```

**SS15 — the matrix, `docs/planning/store-legal-safety-requirements.md` (yours): the Contents, the states' range.**

> ```
> [states](#42-state-law) (UST-01 to UST-59)
> ```

> ```
> [states](#42-state-law) (UST-01 to UST-61)
> ```

**SS16 — the matrix, `docs/planning/store-legal-safety-requirements.md` (yours): section 1's summary counts.**

> ```
> **331 requirement rows:** Apple 69, Google Play 65, US federal 22, US states 59, UK 50, EU 66. Of these, 84 have **no owner** (wholly or for a named part) and 86 do **not apply now**
> ```

> ```
> **333 requirement rows:** Apple 69, Google Play 65, US federal 22, US states 61, UK 50, EU 66. Of these, 84 have **no owner** (wholly or for a named part) and 88 do **not apply now**
> ```

## 11. Who applies what

- **You, in the records batch:** SS1 to SS16, and A06's Work Register row.
- **Then:** the message, revised, goes to Nathan.
- **I read next:** his answers' OD row, and the bounded change's brief.

Status: complete
