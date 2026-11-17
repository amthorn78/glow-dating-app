# DM-84 — OD-68: the card check, the photo check's toggle, and PF02's revision 1.2

- **From:** Dev Manager 5 (`session_01Q789u3CWg6s9pBGXerCQZt`), for App Manager 12, relayed by Nathan (OD-25).
- **Date:** 17 November 2026. Received about 15:53 UTC; finished about 16:11 UTC.
- **Read at:** `21c8fcf5878fd2712feed135f739510aeb258285` of `claude/magical-wozniak-yfmmx2`, exported outside any worktree.
  - `main` is at `cf0ac60` (PR49's merge), the only merge base. No pull request is open.
  - The governing diff since my last read (`8995d37`) is PF02 only (revision 1.2, at `d22f3e8` and `a6b7d48`). `AGENTS.md`, `CLAUDE.md`, PF00, PF01, the manager workflow, my charter and the CI policy are unchanged.
- **Environment:** names only. None of `DATABASE_URL`, `HD_API_KEY`, `GEO_API_KEY`, or any `STREAM_*`, `PG*`, `R2_*`, `CLOUDFLARE_*`, `CF_*` or `RAILWAY_*` name is set. The AWS names are present and were not read.
- **What I changed:** this file only, on `claude/dev-manager`. Notion and GitHub were read, not changed. No call to Stream, a database, HDE, Railway or Cloudflare, and no public web page was fetched.
  - I ran the trusted classifier from `cf0ac60`, extracted outside the worktree, under `python3 -I`.

## 1. The answers

| Item | Verdict |
|---|---|
| 1. OD-68's row | **Approved with conditions: QQ1 to QQ4.** The quotation is faithful. One clause rests on no source: that store billing "gives Glow no card details" (QQ1). A06 goes to Nathan first (QQ2). The toggle's reading is the manager's to record, and I confirm it; the next message tells him in one line. What the toggle does is my default, recorded as such (QQ3). OD-64's row gains an OD-68 note (QQ4) (section 4) |
| 2. The card check | **Approved with conditions: two questions to Nathan first, in the words of section 4, then A05-V2 scoped by his answers.** A06 is a decision now: it decides whether OD-68's card check is in the MVP at all. G-07 is not his decision; it goes live if he chooses a paid plan, and is routed then. One more route, (d), a purchase outside the stores' billing on the US storefront, joins (b) in the research |
| 3. What OD-68 changes | **Approved with conditions.** One bounded change, after his answers (and A05-V2's decision, if research is needed), before P10. It is full scope: it changes the contract's completion list and F05's registry. The staff approval and OD-64's lock wait for ID validation. The toggle's states are my defaults. The carried items and the P11 plan name OD-68 now (QQ5 to QQ10). The OD-61 notes are in six matrix rows, not one (QQ17 to QQ23) (section 5) |
| 4. Records corrections | **Approved with conditions: QQ11 to QQ16.** One more: section 1's "85" rows with no owner has been one too many since 9 November; the count is 84. Section 9's sentences do not wait for item 3 (section 6) |
| 5. No decision message now | **Agreed.** A05-V's record also stands for G-02's detection choice, which OD-68 does not decide (section 7) |
| 6. PF02's revision 1.2 | **Approved as written.** Coverage 185 of 185 (section 8) |
| 7. The sequence | **Agreed, with one step added:** the two questions go to Nathan right after the records batch, before A05-V2's brief (section 9) |
| 8. Notion | **Matches,** with two notes: the status repeats QQ1's unsourced clause, and A06's Work Register row does not yet name OD-68 (section 10) |

## 2. What I read and checked

- **The classification.** The trusted `scripts/change_scope.py` from `cf0ac60`, run with the full SHAs of `cf0ac60` and `21c8fcf` and `--merge-base`, gives `ordinary-docs-only` on 11 paths, with one merge base. No path is outside Markdown or under `.claude/`.
- **The register:** OD-68, OD-61, OD-64 and OD-60, whole; PF01's A06 row.
- **A05-V's record:** its sections 7.4, 8, 10 and 12, and every mention of a card.
- **The matrix:**
  - AP-14, AP-39 to AP-45, GP-38 to GP-45, UST-36, UST-51 to UST-59 and AP-67 to AP-69, whole;
  - G-01, G-02 and G-07, and sections 1, 9 and 10;
  - every mention of OD-61, by script;
  - its counts, by script, at seven commits from `86688d1` to `21c8fcf`, which place the change in the no-owner count at `d461ea5`.
- **The code at `21c8fcf`:**
  - `glow_profiles/requirements.py`, the completion requirements;
  - `glow_domain/identity_verification.py`, the record, the seam and the staff approval's limit;
  - `glow_domain/media.py`, the photo states, F05's transitions and the seams;
  - `glow_profiles/media.py`, `review` and `run_check`, with the check's recorded subject;
  - the contract's completion list (`gapp-api-v1.schema.json`) and the flow registry (`flows-v1.json`).
- **SV2's brief:** D2, D10 and D18.
- **The carried-items file:** the P07, P08, P10 and M07 entries and the OD-64 section. **The P11 plan:** its SV2 entry.
- **PF02's revision 1.2:** the diff from `8995d37`, R09 whole, sections 7, 8 and 9, the header, AM12-13 and AM12-14 in the log, and the coverage, by script.
- **DM-83's words:**
  - PP1 to PP9 are found at the head. The brief is revision 1 with PP1 to PP9, a new revision line and its Sessions entries, and nothing else.
  - PR49's description took my three bullets, and its run and Codex's summary are on its final head, `13785bd`.
- **GitHub:** PR49 merged; no pull request open.
- **Notion:** section 10.

## 3. My own error in this round

- **DM-83 section 7 called the Dev Manager page's DM-83 row a match.** It had seven cells under six headers (AM12-14): every cell after the second sat one column right, and the last was dropped.
- **Why I missed it:** I compared the row's text with the review log, not its cells with the table's headers.
- **What changes in my reads:** a Notion table row is now counted against its table's headers, as PF02-R09's new check asks of the manager. This read did so: DM-83's and DM-84's rows have six cells each.
- **Effect:** none beyond AM12-14's own. The manager found the row when DM-83's answer was written in, and corrected it.

## 4. Items 1 and 2 — OD-68's row, and the card check

**OD-68's row:**
- **The quotation is faithful** to the session's note and to his three answers, including his words as typed ("I want  toggle for this").
- **"Partly supersedes OD-61"** is right. OD-61's staff approval is not superseded: it waits (section 5).
- **One clause rests on no source:** the card check "when the trial is bought through Apple's or Google's billing, which gives Glow no card details (the A05-V record, section 10, and the in-app purchase rows AP-39 and GP-38)".
  - The record's section 10 says only that Stripe Identity is not payment processing, and that store billing does not change that.
  - AP-39 and GP-38 say that paid features must use the stores' billing. Neither says what Glow receives.
  - The clause is probably true, but each claim must trace to its source (PF02-R53). QQ1 says what the rows say, and leaves the rest to the research. Implementation Control's status repeats the clause.
- **The toggle's reading is the manager's to record, and I confirm it.**
  - "We can drop it" gives off at launch, and "toggle" gives something he can switch.
  - OD-60 is his standing instruction that items like this are console settings.
  - It needs no question of its own. The next message tells him in one line, so that he can say if he meant otherwise.
- **What the toggle does is not in his words.** I set it as defaults, recorded as mine and open to his change, as Dev Manager 4 did for OD-61's staff approval (QQ3; section 5).
- **OD-64's row** still reads as if members are verified. Its lock has no trigger in the MVP, and its "Not a full bound" sentence names "the verified face" as a protection the MVP will not have (QQ4).

**The card check: ask Nathan first, then research.** Two answers decide the route and the research's scope.
- **A06, a paid plan at launch.**
  - PF01's A06 default is "no active paid feature; do not buy a plan or invent pricing".
  - A free trial of a paid plan is a paid plan, and OD-68's card check is tied to that trial ("For signup during the trial"; "Free trial of a paid plan").
  - So whether the MVP has a paid plan decides whether the card check is in the MVP at all.
- **What the check is for.**
  - If it is to have a payment method ready for when the trial ends, the store's own trial may do it (route (a)), if the stores require one. That is not yet researched.
  - If it is to make fake or duplicate accounts harder, or to show an adult, Glow needs a result it can see. Nothing on record says store billing gives one, so that needs route (b) or route (d).
  - The consultation's title says "in place of ID verification". His words do not make the card check a completion requirement. Where it sits (a completion requirement, or a step of the trial purchase) follows from this answer.
- **Route (d), not in the consultation:** on the US storefront, the trial is bought outside the stores' billing through a link.
  - AP-42: on the US storefront, links and buttons to other purchase methods are allowed without an entitlement.
  - GP-39: US alternative billing or external links, opt-in, with fees (10% for auto-renewing subscriptions).
  - Glow's own card processor then checks the card as part of the purchase. The research takes it with (b).
- **A05-V2, if his answers need it,** scoped to them:
  - the stores' trial rules: whether a trial needs a payment method, and what the developer receives;
  - the stores' rules on a card check outside their billing used only to verify, and routes (b) and (d) on the US storefront;
  - card-verification services: what a check confirms (a valid card; a name, address or age, if any), the price, and what each keeps;
  - if he chooses a paid plan, the recheck that section 10 asks for when a paid launch is decided: G-07's rows (USF-16, UST-22 to UST-31) and the store subscription rows (AP-39 to AP-45, GP-38 to GP-45), read on 1 November and not rechecked.
- **A06 and G-07.**
  - A06 is a decision now, and it is his. It goes first, with the purpose question.
  - G-07 is not his decision. Its own Timing cell says "Only if Nathan chooses a paid launch (A06)". If he does, the manager routes it as G-07's row proposes (a PF01 §7 "Billing" line, or P08.3's brief scope), with the recheck above.
- **The staff question** goes into the card-check decision message: whether staff may approve a member without the card check, as OD-61 asked for ID.

**The two questions.** My read of these words is this report. The manager sends them after the records batch. They are questions, not a decision message: his answers set the research, and the decision message follows it.

```
Two questions on the card check (OD-68), before any research

1. A paid plan at launch. You chose "free trial of a paid plan". The project plan's default is no paid feature at launch (A06). Does the MVP launch with a paid plan whose free trial starts at signup?
   - If yes: the stores sell the plan through their own billing (in the US they also allow a link to a purchase outside it); subscription law applies when the trial turns into a payment (renewal and cancellation rules); and you set the plan and its price.
   - If no: there is no trial at launch, so there is no card check at launch either.

2. What the card check is for. Which of these must it do? Choose any.
   (a) Make sure a payment method is ready for when the trial ends.
   (b) Make fake or duplicate accounts harder to create.
   (c) Show that the member is an adult.
   When Apple or Google sells the trial, the store takes the payment. Whether Glow learns anything about the card is one of the facts the research would confirm. For (a), the store's own trial may be enough. For (b) or (c), Glow needs a check whose result it can see, outside the stores' billing, and the research would compare the ways to do that.

For your information:
- I have read your "toggle" for the photo check as a switch in the admin console, off at launch, like your other settings. Say if you meant something else.
- Dropping the photo check does not decide whether photos are scanned for known child sexual abuse material. No law the research read requires it, and free scanning programmes exist on their own terms. It stays with the safety work (P07).
```

## 5. Item 3 — what OD-68 changes, and where it lands

**SV2's completion requirements:**
- **The photo requirement stands.** The code asks for at least one photo in state `approved` (`requirements.py`, line 118). Only how a photo reaches `approved` changes while the toggle is off.
- **The identity requirement cannot be met in the MVP.** It asks for `verified` or `staff_approved` (`requirements.py`, lines 122 to 124). No check runs (the seam's fixture adapter passes no one), and the staff approval is off at launch. So no profile can become visible until the requirement changes.
- **When:** nothing is live, so it can wait, but it must land before P10, whose evidence runs onboarding to a visible profile.

**Where it lands: one bounded change,** after Nathan's two answers (and A05-V2's decision, if research is needed).
- It is full scope. The contract's completion list names `identity_verification` (`gapp-api-v1.schema.json`), and F05's registry (`flows-v1.json`) gains the photo transition the toggle needs (below).
- Its brief comes to me first. Until then nothing is built, and the carried items name OD-68 (QQ5 to QQ10).

**The staff approval without verification (D18): it waits.**
- It stands in for identity verification only (D2's fixed limit; `identity_verification.py`, line 51). With no identity requirement, it has nothing to stand in for.
- It does not stand in for the card check unless Nathan says so; the card-check decision message asks him.
- Its code and setting stay. Nothing changes now.

**OD-64's birth-date lock: it waits** until ID validation is added. Nothing changes now (QQ4, QQ8).
- OD-68 opens one gap: a member who is never verified has "one self-service correction", and OD-64's text does not say what follows it. OD-64's own brief settles that (QQ8).

**The photo check's toggle: my defaults** (Dev Manager 5's, not his words; he can change any):
- **The setting:** one in D2's store, on OD-60's pattern, versioned and audited, off at launch.
- **What it covers:** the automated check only (`PhotoCheckPort`). Glow's processing, which strips a photo's metadata, and G-02's seam are not the photo check. Every photo still passes F05's `review`, as now.
- **While it is off:**
  - a photo is approved from `review_pending` by F05's existing `approve` (role `system`), under the toggle's own recorded subject and reason;
  - never under `system:photo-check` with the check's approval reason, so no record says the check approved it;
  - the hold port and a staff restriction still stop the approval, as in `run_check` now.
- **Turning it on:**
  - new photos wait for the check;
  - photos approved while it was off stay shown and go through the check, found by their recorded reason;
  - a photo the check rejects leaves view. F05 has no `system` transition out of `approved` (`restrict_media` is the moderator's), so the bounded change adds one to the registry.
- **Turning it off again:** photos waiting for the check are approved under the toggle's reason.
- **Throughout:** staff act on reports (OD-61's no-staff-review part stands), and `restrict_media` works in both states.

**G-02 is not decided by OD-68.**
- The detection seam is G-02's (`media.py`), configured with none in SV2.
- Dropping the photo check leaves G-02's detection choice where the matrix routes it: P07.1, with an M07 line if a service is chosen.
- A05-V's section 7.4 holds its facts: no federal duty to scan (USF-07), and free programmes on their own terms. Nathan is told in one line (section 4).

**The carried items:** named now, not deleted, since ID validation and the toggle stay possible.
- P07 (QQ5), P08 (QQ6), P10 (QQ7), the OD-64 section (QQ8) and M07 (QQ9);
- the P11 plan's SV2 entry, which states both requirements (QQ10).

**The matrix:** six rows, not one, state OD-61's face match as planned.
- UST-51 to UST-55, in their State cells, with "after OD-61's decision message" in their Owner cells; and AP-67, in its State cell.
- QQ17 to QQ23 add OD-68 to each now. They state a plan that OD-68 sets aside, so they do not wait for the bounded change.
- AP-67's and AP-68's Binds cells describe conditions, and stay.

**A05-V's record:** its sections 7.2 and 8 stay as dated research, and its section 12 note is enough.

## 6. Item 4 — the records corrections

- **Agreed,** in QQ11 to QQ16.
- **Section 1's counts, by script:** 331 rows (Apple 69, Google Play 65, US federal 22, US states 59, UK 50, EU 66); 84 with no owner; 86 not applicable now.
- **The no-owner count has been one too many since 9 November.**
  - The matrix had 85 rows with "No owner" until `d461ea5`, where GP-36 took P09.2 for both parts (SV1; DM-45 13.1).
  - It has had 84 since then, and A05-V's new rows all have owners. The summary kept 85.
- **The not-applicable count:** 81 at `8995d37`, as the summary says, and 86 now. AP-68 and UST-52 to UST-55 are new rows that do not apply now.
- **G-01's Timing cell:** UST-36 now names Act 2026-59 and binds "from 1 January 2027".
- **Section 9:**
  - QQ15 adds the eight new rows to the thresholds sentence, as their rows state them. These are Colorado's biometric provision for any amount of biometric data, Connecticut's act reaching a business that processed consumers' sensitive data, with no number stated, Nebraska's and Minnesota's small-business no-sale rules, and the biometric and health laws with no size threshold.
  - QQ16 adds Alabama to the app-store acts.
- **These do not wait for item 3:** each states rows whose text OD-68 does not touch.

## 7. Item 5 — no decision message now

- **Agreed.** The identity half waits for Nathan's answers, and the photo half for the toggle's first use.
- A05-V's record stands as the research for ID validation later, for the toggle, and for G-02's detection choice (its section 7.4).

## 8. Item 6 — PF02's revision 1.2

- **The texts are as the consultation gives them** (the diff from `8995d37`):
  - R09's rule gains the sentence on a new table row; its check becomes the one quoted, which covers it; its sources gain AM12-14, with a "Changed" line;
  - AM12-13 is in section 7;
  - section 8's bullet and section 9's 1.2 line record both, and the header reads "Revision: 1.2".
- **The placements follow PF02's maintenance rule:**
  - AM12-13's own tool caught it, with no effect (the table refused the write): the log's rule for section 7, as for AM5-20 and AM12-12;
  - AM12-14 broke R09, and its row proposes the sentence.
- **Coverage, by script:** the log holds 185 IDs, AM2-01 to AM12-14. Each appears in PF02, and PF02 names none outside the log.
- **Approved as written.** It needs no further read before PR50 merges, unless the records batch changes a governing text other than in my words.

## 9. Item 7 — the sequence

**Agreed, with the questions added:**
1. The records batch: your disposition and QQ1 to QQ23 (item 4's corrections are QQ11 to QQ16).
2. The two questions to Nathan (section 4), right after the batch. They need no pull request.
3. PR50, as you describe it, merged after the run and Codex's summary on its final head and its checklist. The batch changes no governing text, so my read of PF02 stands.
4. A05-V2's brief to me, if his answers need research; then its prompt, the session and your verification.
5. The decision message on the card check, with the staff question, to me before Nathan.
6. The bounded change, its brief to me first and full scope, before P10; then SV4. Each is named to Nathan before it starts (OD-29).

## 10. Item 8 — Notion (read-only, at about 16:00 UTC)

| Page | What I compared | Result |
|---|---|---|
| Implementation Control, status | Last matched at `21c8fcf`: A05-V integrated, OD-68 recorded, DM-84 | **Match.** It repeats "which gives Glow no card details"; correct it with OD-68's row (QQ1) |
| Its Branches bullet | Four branches, against `git ls-remote` now: `main` `cf0ac60`, `claude/vigilant-ramanujan-jbxqro` `0859532`, the manager branch `21c8fcf`, `claude/dev-manager` `3c0a5fe` | **Match** |
| Its Main bullet | `cf0ac60`, PR49's merge; no open pull request, as GitHub shows | **Match** |
| Its Mistakes log bullet | AM12-01 to AM12-14 at `a6b7d48`; the log has not changed since | **Match** |
| Its procedure summary | The stamp at `a6b7d48`, where PF02 last changed; no governing path changed from `a6b7d48` to `21c8fcf` | **Match** |
| Dev Manager page, `DM-83` and `DM-84` | DM-83 considered (merge `55b8f8a`); DM-84 awaited; six cells each, under the table's six headers | **Match** |
| The register copy | Matched at `21c8fcf`; 68 rows, as the repository; OD-61, OD-64, OD-66 and OD-68 equal in text; OD-66's link pinned at `c7716e3` (DM-83's correction) | **Match.** Nine older rows differ only in link text: the copy writes repository paths as GitHub links |
| Work Register, `M08` | "Coverage of the mistakes log: 180 of 180 at the merge (c7716e3; M08's record, section 12)" (DM-83's correction) | **Match** |
| Work Register, `A05-V`, `A05` and `SV4` | A05-V verified; A05 names OD-68 and DM-84; SV4 planned | **Match** |
| Work Register, `A06` | "Default no active paid feature; obtain monetization choice before implementing/activating real purchases." It does not name OD-68, which raises it | **Not yet updated.** It matches the repository's A06 row; it should name OD-68 and the question at the sync that sends the questions |

## 11. The words

**QQ1 — the register, `docs/continuity/owner-directions.md` (yours): OD-68's State: what store billing gives Glow.**

> ```
> how a card check works when the trial is bought through Apple's or Google's billing, which gives Glow no card details (the A05-V record, section 10, and the in-app purchase rows AP-39 and GP-38);
> ```

> ```
> how a card check works when the trial is bought through Apple's or Google's billing, where the store takes the payment (AP-39, GP-38; whether Glow then learns anything about the card is confirmed by no source read yet);
> ```

**QQ2 — the register, `docs/continuity/owner-directions.md` (yours): OD-68's State: A06 first.**

> ```
> what a paid plan means for A06;
> ```

> ```
> whether the MVP launches with a paid plan (A06, whose default is no paid feature) and what the card check is for, two questions put to Nathan first (DM-84);
> ```

**QQ3 — the register, `docs/continuity/owner-directions.md` (yours): OD-68's State: the toggle's reading and defaults.**

> ```
> **The automated photo check is dropped for the MVP, with a toggle to turn it on** (App Manager 12's reading: a console setting on OD-60's pattern, off at launch).
> ```

> ```
> **The automated photo check is dropped for the MVP, with a toggle to turn it on** (App Manager 12's reading, which Dev Manager 5 confirms as following his words and OD-60: a console setting on OD-60's pattern, off at launch). **Defaults set by Dev Manager 5, not his words** (he can change any; DM-84): while the toggle is off, a photo still passes Glow's processing and G-02's seam, and is then approved under the toggle's own recorded reason, never recorded as the check's approval; turning it on makes new photos wait for the check and sends the photos already shown through it, each staying shown unless the check rejects it.
> ```

**QQ4 — the register, `docs/continuity/owner-directions.md` (yours): OD-64's State: the lock under OD-68.**

> ```
> In force. **The probing the two-way rule allows is bounded by field**
> ```

> ```
> In force; **under OD-68 its birth-date lock waits** (no member is identity-verified in the MVP, so the lock waits until ID validation is added, and until then the verified face is not among the protections named under "Not a full bound"). **The probing the two-way rule allows is bounded by field**
> ```

**QQ5 — the carried-items file, `docs/planning/carried-to-later-items.md` (yours): P07's entry.**

> ```
> P07 plans what a member can do when the automated identity check fails: a retry, and an appeal its one operator answers (OD-23).
> ```

> ```
> P07 plans what a member can do when the automated identity check fails: a retry, and an appeal its one operator answers (OD-23). **OD-68 (17 November 2026):** for the MVP no identity check runs and the automated photo check is off behind a console toggle, so the staff approval without identity verification, its setting and the failed-check path wait until ID validation is added; P07's console holds the photo check's toggle, and any staff step the card check needs waits for its decision.
> ```

**QQ6 — the carried-items file, `docs/planning/carried-to-later-items.md` (yours): P08's entry.**

> ```
> The identity verification company's copy of a member's ID and selfie is deleted on the schedule Nathan's decision sets, and on account deletion.
> ```

> ```
> The identity verification company's copy of a member's ID and selfie is deleted on the schedule Nathan's decision sets, and on account deletion. **OD-68:** no identity verification company is used for the MVP, so this waits until ID validation is added; whatever the card check keeps, at Glow or at a processor, is P08's to place once its design is decided.
> ```

**QQ7 — the carried-items file, `docs/planning/carried-to-later-items.md` (yours): P10's entry.**

> ```
> Onboarding adds the identity verification step before a profile can show, and the owner sees the completion read's missing requirements.
> ```

> ```
> Onboarding adds the identity verification step before a profile can show, and the owner sees the completion read's missing requirements. **OD-68:** for the MVP there is no identity verification step; the card check's place in onboarding waits for its decision, and SV2's completion requirements change first (DM-84).
> ```

**QQ8 — the carried-items file, `docs/planning/carried-to-later-items.md` (yours): the OD-64 section.**

> ```
> The birth date's lock waits on the identity verification company (OD-61's decision message).
> ```

> ```
> The birth date's lock waits until ID validation is added, which OD-68 sets aside for the MVP; the brief settles what follows the one self-service correction for a member who is never verified.
> ```

**QQ9 — the carried-items file, `docs/planning/carried-to-later-items.md` (yours): M07's entry.**

> ```
> two services to cost: an identity verification company (a government photo ID with a selfie matched to it, for every member) and an automated photo check. Nathan approves each line before any account is created (OD-50).
> ```

> ```
> two services to cost: an identity verification company (a government photo ID with a selfie matched to it, for every member) and an automated photo check. Nathan approves each line before any account is created (OD-50). **OD-68:** neither is used for the MVP; the photo check's line returns before its toggle is first turned on, and a card check's cost, if its design needs a service, is added after its decision.
> ```

**QQ10 — the P11 plan, `docs/testing/p11-deferred-acceptance.md` (yours): SV2's entry.**

> ```
> The verification company and the photo check's service are wired only after Nathan's decision and their M07 lines (OD-50).
> ```

> ```
> The verification company and the photo check's service are wired only after Nathan's decision and their M07 lines (OD-50). **OD-68 (17 November 2026):** neither is used for the MVP; SV2's completion requirements change before P10 (DM-84), and P11 wires a service only after its decision and its M07 line.
> ```

**QQ11 — the matrix, `docs/planning/store-legal-safety-requirements.md` (yours): the Contents, Apple's range.**

> ```
> [Apple App Store](#2-apple-app-store) (AP-01 to AP-66)
> ```

> ```
> [Apple App Store](#2-apple-app-store) (AP-01 to AP-69)
> ```

**QQ12 — the matrix, `docs/planning/store-legal-safety-requirements.md` (yours): the Contents, the states' range.**

> ```
> [states](#42-state-law) (UST-01 to UST-51)
> ```

> ```
> [states](#42-state-law) (UST-01 to UST-59)
> ```

**QQ13 — the matrix, `docs/planning/store-legal-safety-requirements.md` (yours): section 1's summary counts.**

> ```
> **320 requirement rows:** Apple 66, Google Play 65, US federal 22, US states 51, UK 50, EU 66. Of these, 85 have **no owner** (wholly or for a named part) and 81 do **not apply now**
> ```

> ```
> **331 requirement rows:** Apple 69, Google Play 65, US federal 22, US states 59, UK 50, EU 66. Of these, 84 have **no owner** (wholly or for a named part) and 86 do **not apply now**
> ```

**QQ14 — the matrix, `docs/planning/store-legal-safety-requirements.md` (yours): G-01's Timing cell.**

> ```
> California and Alabama (unconfirmed) 1 January 2027
> ```

> ```
> California and Alabama 1 January 2027
> ```

**QQ15 — the matrix, `docs/planning/store-legal-safety-requirements.md` (yours): section 9, the privacy laws' thresholds.**

> ```
> The comprehensive privacy laws read bind at thresholds Glow does not meet, except Texas's no-sale rule for small businesses (UST-45) and Colorado's minors duties (UST-41).
> ```

> ```
> The comprehensive privacy laws read bind at thresholds Glow does not meet, except Texas's, Nebraska's and Minnesota's no-sale rules for small businesses (UST-45, UST-58, UST-59), Colorado's minors duties (UST-41) and its biometric provision, which reaches a controller of any amount of biometric data (UST-55), and Connecticut's act from 1 July 2026, which reaches a business that controlled or processed consumers' sensitive data in the preceding calendar year, with no number stated (UST-57). The state biometric and consumer health data laws read state no size threshold (UST-51 to UST-54, UST-56).
> ```

**QQ16 — the matrix, `docs/planning/store-legal-safety-requirements.md` (yours): section 9, the app-store acts.**

> ```
> App-store age acts: Texas now, California 1 January 2027, Utah 6 May 2027, Louisiana 1 July 2027 (UST-32 to UST-35).
> ```

> ```
> App-store age acts: Texas now, California and Alabama 1 January 2027, Utah 6 May 2027, Louisiana 1 July 2027 (UST-32 to UST-36).
> ```

**QQ17 — the matrix, `docs/planning/store-legal-safety-requirements.md` (yours): UST-51's Binds cell.**

> ```
> OD-61 (10 November 2026) plans identity verification that matches a selfie to the ID photo, through a verification company [corrected at the A05-V recheck: this said "none planned"];
> ```

> ```
> OD-61 (10 November 2026) planned identity verification that matches a selfie to the ID photo, through a verification company [corrected at the A05-V recheck: this said "none planned"], and OD-68 (17 November 2026) sets it aside for the MVP;
> ```

**QQ18 — the matrix, `docs/planning/store-legal-safety-requirements.md` (yours): UST-51's Owner and State cells.**

> ```
> P08 (consent wording), after OD-61's decision message [A05-V: was "—"] | Not applicable at `f40f1d7` (nothing scans a face); OD-61 plans the face match, and the consent waits on its decision message [A05-V: was "Not applicable"]
> ```

> ```
> P08 (consent wording), if ID validation is added (OD-68) [A05-V: was "—"] | Not applicable at `f40f1d7` (nothing scans a face); OD-68 (17 November 2026) sets the face match aside for the MVP, and the consent comes with ID validation if it is added [A05-V: was "Not applicable"]
> ```

**QQ19 — the matrix, `docs/planning/store-legal-safety-requirements.md` (yours): UST-52's Owner and State cells.**

> ```
> after the purpose expires | P08 (consent wording, retention), after OD-61's decision message | Not applicable at `f40f1d7` (nothing scans a face); OD-61 plans the face match |
> ```

> ```
> after the purpose expires | P08 (consent wording, retention), if ID validation is added (OD-68) | Not applicable at `f40f1d7` (nothing scans a face); OD-68 (17 November 2026) sets the face match aside for the MVP |
> ```

**QQ20 — the matrix, `docs/planning/store-legal-safety-requirements.md` (yours): UST-53's Owner and State cells.**

> ```
> reasonably necessary | P08 (consent wording, retention), after OD-61's decision message | Not applicable at `f40f1d7` (nothing scans a face); OD-61 plans the face match |
> ```

> ```
> reasonably necessary | P08 (consent wording, retention), if ID validation is added (OD-68) | Not applicable at `f40f1d7` (nothing scans a face); OD-68 (17 November 2026) sets the face match aside for the MVP |
> ```

**QQ21 — the matrix, `docs/planning/store-legal-safety-requirements.md` (yours): UST-54's Owner and State cells.**

> ```
> deletion; processor contracts | P08 (consent wording, retention), after OD-61's decision message | Not applicable at `f40f1d7` (nothing scans a face); OD-61 plans the face match |
> ```

> ```
> deletion; processor contracts | P08 (consent wording, retention), if ID validation is added (OD-68) | Not applicable at `f40f1d7` (nothing scans a face); OD-68 (17 November 2026) sets the face match aside for the MVP |
> ```

**QQ22 — the matrix, `docs/planning/store-legal-safety-requirements.md` (yours): UST-55's Owner and State cells.**

> ```
> sale; processor terms | P08 (consent wording, retention), after OD-61's decision message | Not applicable at `f40f1d7` (nothing scans a face); OD-61 plans the face match |
> ```

> ```
> sale; processor terms | P08 (consent wording, retention), if ID validation is added (OD-68) | Not applicable at `f40f1d7` (nothing scans a face); OD-68 (17 November 2026) sets the face match aside for the MVP |
> ```

**QQ23 — the matrix, `docs/planning/store-legal-safety-requirements.md` (yours): AP-67's State cell.**

> ```
> Not planned at `f40f1d7` (no face data); OD-61 plans the selfie match, and no brief names these terms (gap G-10)
> ```

> ```
> Not planned at `f40f1d7` (no face data); OD-61 planned the selfie match, which OD-68 (17 November 2026) sets aside for the MVP; no brief names these terms (gap G-10)
> ```

## 12. Who applies what

- **You, in the records batch:** QQ1 to QQ23; then the two questions to Nathan.
- **Nothing here needs another read before PR50 merges,** unless the batch changes a governing text other than in my words.
- **I read next:** A05-V2's brief (if his answers need research), the card-check decision message, and the bounded change's brief.

Status: complete
