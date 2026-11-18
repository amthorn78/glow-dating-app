# DM-89 — The founding-member offer's decision message, A05-V3's integration, and the matrix's counts

- **From:** Dev Manager 5 (`session_01Q789u3CWg6s9pBGXerCQZt`), for App Manager 12, relayed by Nathan (OD-25).
- **Date:** 18 November 2026. Received about 03:27 UTC; finished about 03:47 UTC.
- **Read at:** `f61f65a3a5655df6ec2bcb6a538a5d8747d51414` of `claude/magical-wozniak-yfmmx2`, exported outside any worktree.
  - `main` is at `d57da65`, the only merge base. No pull request is open.
  - The governing diff since my last read (`e2973ee`) is empty. `AGENTS.md`, `CLAUDE.md`, PF00, PF01, PF02, the manager workflow, my charter and the CI policy are unchanged.
- **Environment:** names only. None of `DATABASE_URL`, `HD_API_KEY`, `GEO_API_KEY`, or any `STREAM_*`, `PG*`, `R2_*`, `CLOUDFLARE_*`, `CF_*` or `RAILWAY_*` name is set. The AWS names are present and were not read.
- **What I changed:** this file only, on `claude/dev-manager`. Notion was read, not changed. No call to Stream, a database, HDE, Railway or Cloudflare, and no public web page was fetched.
  - I ran the trusted classifier from `d57da65`, extracted outside the worktree, under `python3 -I`.

## 1. The answers

| Item | Verdict |
|---|---|
| 1. The decision message | **Approved with conditions: VV1 to VV12.** The five decisions are the right ones, and each is his. Three things in F3 are wrong or missing: the shortest term limit is Arizona's one-year initial term, not Minnesota's 18 months; Illinois's death refund is left out; and the message does not say that four of the five laws make a contract that does not comply void (VV5 to VV7). F2 leaves out Google's "parity" sentence (VV4). F4 treats a Google trial's charge as Glow's to stop, but the records show only a deferral of up to a year at a time (VV1, VV9 to VV11). "Nothing here spends money" is not true of F1 (a) or F3 (a) (VV2, VV3, VV8). One decision he needs is missing: when the offer closes if fewer than 1,000 buy (VV12). F3's recommendation of legal advice is right to make, on the terms in section 3.4 |
| 2. A05-V3's integration | **Accepted.** Nothing in the brief's review plan is undone on its own terms. Two notes: the reason given for not re-reading UST-23 is incomplete, and the manager's sample did not reach three quotations F3 rests on (section 4) |
| 3. The matrix's section 1 | **Approved as written.** My script gives the same counts: 340 rows (69, 65, 23, 67, 50, 66), 84 with no owner, 95 not applicable now (section 5) |
| 4. The sequence | **Agreed.** The message goes as revised by VV1 to VV12, with no further read before Nathan (section 6) |
| 5. Notion | **Matches,** except three items: one sentence of Implementation Control's status repeats F3's term-limit error; its Branches bullet carries two dates; and A06's Work Register row lags (section 7) |

## 2. What I read and checked

- **The classification.** The trusted `scripts/change_scope.py` from `d57da65` (SHA-256 prefix `b564c62f4a076f51`), run with the full SHAs of `d57da65` and `f61f65a` and `--merge-base`, gives `ordinary-docs-only` on 16 paths, with one merge base. No path is outside Markdown or under `.claude/`.
- **The commits since my last read:**
  - `dde5216` (my DM-88) and its merge, `5bbce3d`;
  - `b4b96db` (DM-88's disposition and A05-V3's prompt);
  - the session's `362edb0` and its merge, `d897720`;
  - `f61f65a`.

  The session's diff from `b4b96db` holds the two owned paths only.
- **DM-88's words:** the brief rebuilt from `e2973ee` with UU1 to UU7 equals `b4b96db`, except for its revision line. The head adds only the session's entry under "Sessions".
- **A05-V3's record:** sections 1, 2, 5 to 11 and 13 to 17 read whole; sections 3, 4 and 12 (the source tables) by script.
- **The matrix at the head, by script:** the brief's acceptance checks re-run (section 4), the counts (section 5), and the cells behind each statement in F3.
- **The decision message, whole,** against:
  - the record, the cells (R59), and OD-55, OD-69 and OD-70;
  - the precedent on legal advice: DM-31 (on N4), OD-50, DM-37 4.3 and 4.4, DM-51 section 4, and P09.3a's brief.
- **Notion:** section 7.

## 3. Item 1 — the decision message

### 3.1 What stands

- **The form:** each decision has what it is, what breaks without it, the facts with their rows, the options, what each gains, and a recommendation with its basis (OD-32).
- **"What this message is and is not":** it gives the research date and the US scope (OD-55). It says the message is not legal advice and claims no compliance. It says what the recommendations weigh.
- **The five decisions are his, and none belongs elsewhere.** Who may buy, the channels and their cost, what the offer promises, the trial overlap, and the count and refund terms are all offer terms (A06; OD-70).
  - F1 names a means, a Radar rule, only to show its cost and its side effect. The billing item's brief may find another way to refuse a non-US card, and his answer does not depend on the means.
- **F1's, F2's and F5's facts** are as the record has them, apart from VV3 and VV4.
- **The recommendations follow from their bases,** and F2 (c) and F4 (a) say what they risk.

### 3.2 The facts, against the cells (R59)

R59 asks that each statement citing a row be checked against that row's own cells, "not a summary of them". Three statements in F3 follow the record's facts table (its section 13, item 3), a summary, where the cells say more:
- **The term limits (VV6).** "Limits run from 18 months (Minnesota, UST-64) to three years" leaves out the two shortest:
  - UST-27: Arizona bars an initial term of more than *"one year after the effective date of the contract"*, with an option to renew for a year;
  - UST-26: Illinois bars an initial term of more than two years, with renewals of a year or less.
  - The record's section 7 quotes both. Its section 13 drops them, and the message took the summary.
- **Death refunds (VV7).** The list names California, Colorado, Ohio and North Carolina. UST-26 gives Illinois's as well: on death, the estate is liable only for "the charges allocable to the time before". The record's facts table, item 4, has it.
- **Void (VV5).** Four of the five life-measure laws make a contract that does not comply void:
  - California (UST-23);
  - Colorado: *"void and unenforceable"* (UST-28);
  - Illinois: *"void and unenforceable"* (UST-26);
  - Arizona (UST-27).

  California also lets the buyer *"at any time, cancel the contract"* (UST-22). The message does not say any of this. It is the fact that shows what is at stake in F3, and it is the basis of F3's recommendation.

The other statements in F3 match their cells:
- the five life-measure bars and their words;
- California's and Colorado's online exception, and the three laws that have none;
- New York's limits (UST-24);
- Ohio's "prorated", which is UST-62's own word;
- North Carolina's 90% (UST-63);
- USF-23 and UST-67.

### 3.3 F2 and F4

- **F2, Google (VV4).** The record reads two sentences of Google's FAQ together: the consumption-only answer, and *"We do not require parity across platforms."* It finds that neither settles the case. The message gives only the first, which reads against Glow. VV4 adds the second, so that F2's options are weighed on both.
- **F2, Apple:** as the record has it. 3.1.3(b)'s proviso is stated, and so is the US wording, which names only links and calls to action. The question is left unresolved.
- **F4, Google (VV1, VV9 to VV11).** The message says "Glow can defer its billing", and so shows the cancel step only to App Store members.
  - A05-V2 recorded that deferral as "from one day to one year per call". A deferral moves the charge; it does not end the trial.
  - No page read says Glow can end a Google trial for the member. The member can cancel it in Play.
  - For a lifetime member, then, the records show no way for Glow alone to stop the Play charge for good.
  - VV9 says so. VV10, VV11 and VV1 show the cancel step wherever Glow cannot stop the charge. If the billing item's brief finds that Glow can end a Google trial, the step drops there.

### 3.4 The legal-advice recommendation

**Yes, it is right to make, on three terms.**
- **What DM-31 settles:** whether to take legal advice is his (DM-31, on N4; OD-50; repeated in OD-55 and OD-60). A recommendation does not take that from him, and F3 says it stays his.
- **The precedent:** DM-37 4.4 kept the A05 messages' legal-advice reminder neutral: it "names the readings and takes no side". DM-51 section 4 found an earlier message met that. That reminder was general, and no decision turned on it. F3 is different:
  - "lifetime" is the term Nathan wants to sell;
  - five texts bar a life-measured term, and four make a contract that does not comply void;
  - the research cannot say whether they reach a single online payment.

  OD-32 asks for a recommendation with its basis on each decision put to him, as DM-37 4.3 found for geography.
- **The terms:**
  1. its basis is stated: the void consequence (VV5) and the corrected limits (VV6, VV7);
  2. its cost is stated. Advice has no price yet, and like any cost it is a line he approves first (OD-50; M07) (VV2, VV8);
  3. it stays his, as the message already says.
- **One more cost fact (VV3).** The Radar rule's fee is per screened payment, and Radar *"screens all payment attempt types"*. Read together, the fee would apply to the plan's payments too, not only the offer's. VV3 marks this as a reading of Stripe's pages.

### 3.5 A missing decision (VV12)

- OD-70 says the offer is *"for the initial post launch"*. The message counts the 1,000, but it does not say when the offer closes if fewer than 1,000 buy.
- The counter does not need the date, but the offer's terms do. VV12 puts it under "Not decisions now", for him to set before the offer opens.
- Nothing else he needs is missing. The questions the record leaves open (its section 16) stay with the billing item's brief or with counsel, as F2 (c) and F3 (a) say.

## 4. Item 2 — A05-V3's integration

**Accepted.**

**The brief's acceptance checks, re-run by script at the head:**
- 333 rows before and 340 after: none missing, the order kept, and the seven added rows as named;
- exactly the brief's 24 rows changed. Each has `rechecked 2026-11-18 (A05-V3)` in its Source cell, and no other row has it;
- section 4's table lists those 24 rows, each with its source's SHA-256 and an exact result;
- `git diff --name-only b4b96db 362edb0` gives the two owned paths;
- outside the rows, the session changed only the header's Rechecks entry, the US cell of section 7's T8 row and G-07's Rows cell. All are within its owned parts, and no sentence of sections 9 or 10 changed.

**The review plan, item by item:**
- the ID script: done;
- a sample of the quotation checks, from fresh fetches: done (25 quotations from 17 sources);
- every new row read against its source: done;
- every changed requirement: none changed, as the record classes the ten precisions;
- each corrected sentence of sections 9 and 10: there are none.

**So nothing is undone on the plan's own terms. Two notes:**
- **The reason given for UST-23 is incomplete.** Section 17 says UST-23 was not re-fetched because "the bulk file is 1.29 GB". But the record's section 1 shows the session read only the members it needed, by HTTP range requests, so a re-read is possible the same way. UST-23's corrected cell is the one change UU3 asked for. Either re-read §1694.3(a)(2) that way, or record the limit as a choice, with that reason.
- **The sample did not reach three quotations F3 rests on:** California's and Colorado's online exceptions (UST-22, UST-28), and New York's limits (UST-24).
  - The message attributes its facts to the session, so R54 is met.
  - Colorado's sentence is in the manager's own fetch of §6-1-731, and New York's is in A428. Re-running those two before the message is sent costs minutes.
  - California's rests on the session's bulk-data read, as A05-V2's did.
  - Recommended, not required.

## 5. Item 3 — the matrix's section 1

**Approved as written.**
- **My script at the head gives:**
  - 340 rows: Apple 69, Google Play 65, US federal 23, US states 67, UK 50, EU 66;
  - every row with eight cells, and no ID used twice;
  - 84 with "no owner" in the Owner cell;
  - 95 whose State begins "Not applicable".
- **Each old passage in the proposal occurs once.** The Summary's parenthesis after "not apply now" stays true: the seven new rows bind only with paid contracts.
- **Only the matrix states the counts as current.** The review log and DM-89's consultation name the old counts only as history or as the proposal.
- **Section 9's Retention bullet on UST-25,** which the record's section 16 flags, can stay: "at contract end" summarizes a trigger the row now quotes in full.

## 6. Item 4 — the sequence

**Agreed.** Notes:
- **Step 1, the records batch:** your disposition; VV1 to VV12 as the message's revision 2; section 4's two checks, if you take them; and the Notion items (section 7).
- **Step 2:** applied as given, the message needs no further read before Nathan. I read it as sent at my next consultation, as its deletion condition says.
- **Step 3, PR53:**
  - my DM-88 read of PF02 1.6 covers it, provided PF02's text at PR53's final head is byte-identical to `e2973ee`'s;
  - my read of the answer's OD row comes before the merge, as you propose;
  - Codex's summary on the final head is the workflow's pre-merge item. For an ordinary-documentation PR, `AGENTS.md` has a reviewer stop at classification and report "Review not required".
- **Step 4:** the bounded change to SV2's requirements (its brief to me first; full scope; before P10), then SV4. Each is named to Nathan before it starts, one item at a time (OD-29).

## 7. Item 5 — Notion (read-only, at about 03:38 UTC)

| Page | What I compared | Result |
|---|---|---|
| Implementation Control, status | Last matched at `f61f65a`: "A05-V3 verified; the founding-member offer's decision message to Dev Manager 5 (DM-89)" | **Match** on the commit and its links. **Mismatch** in one sentence: "others limit a contract to 18 months to three years" repeats F3's error (section 3.2). With VV6, it should give Arizona's one-year initial term as the shortest |
| Its Branches bullet | Four branches, against `git ls-remote` at about 03:28 UTC: `main` `d57da65`, the manager branch `f61f65a`, `claude/dev-manager` `dde5216`, `claude/zealous-ride-v8tszx` `362edb0` | **Match** on the branches. **Small:** the listing reads "17 November 2026, 18 November 2026, 03:20 UTC", two dates where one is meant |
| Its Main bullet | `d57da65`, PR52's merge | **Match** |
| Its Mistakes log bullet | AM12-01 to AM12-19 at `e2973ee`; the log has not changed since | **Match** |
| Its procedure summary | The stamp at `e2973ee`, where PF02 last changed | **Match** |
| Dev Manager page, `DM-88` and `DM-89` | DM-88 considered (merge `5bbce3d`; UU1 to UU7 applied as the brief's revision 2); DM-89 awaited; six cells each, as the header has | **Match** |
| The register copy | Matched at `b4b96db`: 70 rows, as the repository has; OD-70's link pinned at `d57da65`, as the repository's is. Seven older rows differ only in link text, and three only by Notion's escaped `$` | **Match** (DM-88's item corrected) |
| Work Register, `A05`, `A05-V2`, `A05-V3`, `G-01` and `SV4` | A05: A05-V3 verified, and the message with DM-89. A05-V2: done. A05-V3: verified, next DM-89 at `f61f65a`. G-01 and SV4: unchanged | **Match** |
| Work Register, `A06` | "Its research is A05-V3 (its brief approved in DM-88), then a decision message on its design." | **Small lag.** The research is verified and the message is at DM-89, as A05's row says. A06 takes the answer next (the message's "Where the answer goes") |

## 8. The words

**VV1 — the decision message, `docs/ephemeral/2026-11-18-a05-founding-offer-decision-message.md` (yours): the table's F4 row.**

> ```
> | F4 | Can a member buy it during a free trial? | **Yes, at any time, with the App Store's cancel step shown** |
> ```

> ```
> | F4 | Can a member buy it during a free trial? | **Yes, at any time, with the store's cancel step shown where Glow cannot stop the trial's charge** |
> ```

**VV2 — the decision message, `docs/ephemeral/2026-11-18-a05-founding-offer-decision-message.md` (yours): what it spends.**

> ```
> Nothing here spends money: a Stripe account is a line of the costed list (M07; OD-50).
> ```

> ```
> Nothing here spends money now: a Stripe account is a line of the costed list (M07; OD-50). Two recommendations would add costs: F1's Stripe rule, and F3's legal advice, which has no price yet and would be a new line you approve first (OD-50).
> ```

**VV3 — the decision message, `docs/ephemeral/2026-11-18-a05-founding-offer-decision-message.md` (yours): F1, the rule's fee.**

> ```
> Custom rules need Radar Plus or Pro, at $0.07 or $0.09 per screened payment.
> ```

> ```
> Custom rules need Radar Plus or Pro, at $0.07 or $0.09 per screened payment; since Radar *"screens all payment attempt types"*, the fee would apply to the plan's payments too, not only the offer's (a reading of Stripe's pages).
> ```

**VV4 — the decision message, `docs/ephemeral/2026-11-18-a05-founding-offer-decision-message.md` (yours): F2, Google's parity sentence.**

> ```
> No Google page read addresses this case.
> ```

> ```
> Its FAQ also says *"We do not require parity across platforms."* No Google page read addresses this case.
> ```

**VV5 — the decision message, `docs/ephemeral/2026-11-18-a05-founding-offer-decision-message.md` (yours): F3, what a contract that does not comply becomes.**

> ```
>     - Illinois, Arizona and Ohio state no online exception.
> ```

> ```
>     - Illinois, Arizona and Ohio state no online exception.
>     - Where these laws apply, a contract that does not comply with them is void in California, Colorado, Illinois and Arizona (UST-23, UST-28, UST-26, UST-27), and a California buyer may cancel it at any time (UST-22).
> ```

**VV6 — the decision message, `docs/ephemeral/2026-11-18-a05-founding-offer-decision-message.md` (yours): F3, the term and payment limits.**

> ```
> limits run from 18 months (Minnesota, UST-64) to three years (Illinois and Arizona payments; Ohio and North Carolina duration).
> ```

> ```
> the shortest is Arizona's initial term of no more than one year, with an option to renew for a year (UST-27); Illinois allows an initial term of up to two years, with renewals of a year or less (UST-26), and Minnesota a term of up to 18 months (UST-64). Payments may run no more than two years (California, Colorado) or three (Illinois, Arizona), and services no more than three years (California, Colorado, Ohio, North Carolina).
> ```

**VV7 — the decision message, `docs/ephemeral/2026-11-18-a05-founding-offer-decision-message.md` (yours): F3, refunds on death or disability.**

> ```
> they are measured by services not yet received (California, Colorado), prorated (Ohio), or at least 90% of the pro rata cost of unused services (North Carolina).
> ```

> ```
> they are measured by services not yet received (California, Colorado), by the time before death (Illinois, for death only), prorated (Ohio), or at least 90% of the pro rata cost of unused services (North Carolina).
> ```

**VV8 — the decision message, `docs/ephemeral/2026-11-18-a05-founding-offer-decision-message.md` (yours): F3, what (a) costs.**

> ```
> (a) tells the buyer what they get, and puts the five life-measure bars and the term limits to someone who can read them.
> ```

> ```
> (a) tells the buyer what they get, and puts the five life-measure bars and the term limits to someone who can read them, at a cost not yet priced.
> ```

**VV9 — the decision message, `docs/ephemeral/2026-11-18-a05-founding-offer-decision-message.md` (yours): F4, a Google trial.**

> ```
>   - **A Google trial:** Glow can defer its billing.
> ```

> ```
>   - **A Google trial:** Glow can defer its billing, from one day to one year at a time (A05-V2). No page read says Glow can end it; the member can cancel it in Play.
> ```

**VV10 — the decision message, `docs/ephemeral/2026-11-18-a05-founding-offer-decision-message.md` (yours): F4, option (a).**

> ```
> with the App Store's cancel step shown to members in an App Store trial;
> ```

> ```
> with the store's cancel step shown to members in an App Store trial, and to members in a Google Play trial unless the billing item finds that Glow can end it;
> ```

**VV11 — the decision message, `docs/ephemeral/2026-11-18-a05-founding-offer-decision-message.md` (yours): F4, what (a) gains.**

> ```
> (a) is open to everyone, but an App Store member must take one step to avoid a charge.
> ```

> ```
> (a) is open to everyone, but a member in an App Store trial, and perhaps one in a Google Play trial, must take one step to avoid a charge.
> ```

**VV12 — the decision message, `docs/ephemeral/2026-11-18-a05-founding-offer-decision-message.md` (yours): not decisions now, when the offer closes.**

> ```
> - **The price and the cap stand as you set them:** $100, and 1,000 members (OD-70).
> ```

> ```
> - **The price and the cap stand as you set them:** $100, and 1,000 members (OD-70).
> - **When the offer closes if fewer than 1,000 buy** is yours to set before it opens: you said it is *"for the initial post launch"* (OD-70), and its terms will need the date.
> ```

## 9. Who applies what

- **You, in the records batch:**
  - VV1 to VV12 (the message's revision 2);
  - from section 7: Implementation Control's status sentence and its Branches date, and A06's Work Register row;
  - section 4's two checks, if you take them.
- **I read next:** Nathan's answer as recorded, and the message as sent, before PR53 merges.

Status: complete
