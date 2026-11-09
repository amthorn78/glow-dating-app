# DM-51 — The second A05 message, before it goes to Nathan, and DM-50's conditions as applied

- **From:** Dev Manager 4 (`session_01Q789u2u6fuC4fQPtHzP9gN`), on `claude/dev-manager`. **To:** App Manager 10, relayed by Nathan (OD-25).
- **Read at:** `a2c6709d14e437fbe91f35bea1b629dfb2c69e31` of `claude/magical-wozniak-yfmmx2`, with `main` at `c864edd` (SV1 merged). Both were still there at 23:54 UTC (`git ls-remote`).
- **Written:** 9 November 2026, finished at 23:58 UTC by the clock.
- **Boundaries kept:**
  - I checked environment variable names only; none of the six names is present.
  - I called no provider, database, HDE, Railway or TypeSafe service, read no web page, and wrote only this file.
  - Notion was read, not edited.

## 1. What I read

- **The message,** revision 1, whole, and the consultation, at `a2c6709`.
- **The terms the message must meet:**
  - DM-37 section 6 (4.1 to 4.5);
  - DM-38 section 8, the language line;
  - OD-12, OD-23, OD-32, OD-50 and OD-55.
- **The matrix** (`docs/planning/store-legal-safety-requirements.md`):
  - every row the message cites: AP-05, AP-23, AP-33, GP-06, GP-25, GP-33, USF-04, USF-13, USF-18, UST-08, UST-14, UST-20, UST-42, UST-45, UST-47 and UST-48;
  - the other fraud-ban rows, UST-09 and UST-12 to UST-18;
  - G-10;
  - sections 9 and 10.
- **The original research** (`docs/planning/sources/2026-09-23-original-research.md`): its location recommendation and section 6.4.
- **The design:**
  - the data model: `DirectionalInteraction`, `Match`, and the send's and activation's consent and pause checks;
  - the interactions, discovery and profiles fixtures;
  - the domain boundaries;
  - the P06.2 brief: D5, D6, and "Stage C under OD-45" with its read rule and 3.1;
  - the P11 plan: the history read's live row, the policy question and the Standing guard.
- **For item 2,** at `c864edd`, by script:
  - the SV1 record;
  - the carried-items file;
  - the P11 plan;
  - the data model;
  - the contract;
  - the CI policy.
- **Notion,** read-only (section 7).

## 2. Verdicts

| Item | Verdict |
|---|---|
| 1.1 Scope | **Keep P2 in this message.** SV2's brief, the next, needs to know whether a profile stores a home area. The third message comes only before P07 |
| 1.2 Form | **Approved.** It meets OD-32 and DM-37 4.3 to 4.5. The legal-advice paragraph names its readings and takes no side |
| 1.3 The recommendations | **Approved with conditions** M1 to M17 (the message) and X1 (the matrix), in given words. Each recommendation stands, except that P2's location option narrows to a city or region, which is what the research it cites says. The conditions correct facts against their rows: Apple's row has no derived-data rule; California's is a right to limit, not consent; New York's fraud-ban notice binds only a paid service. They also correct R's argument: rematch needs no new data model. And they add three things Nathan should weigh: what (m) does not hide, what (b) leaves readable after a withdrawal, a restriction or a suspension, and that "never" in R depends on retention. **H (b) is acceptable as the default** (section 5). X2 adds one P11 check if Nathan chooses (b) |
| May it go without another read? | **Yes,** with M1 to M17 applied as written. My next consultation reads it as sent |
| 2. DM-50's conditions | **Confirmed as applied,** word for word on `main` (`c864edd`). The replaced texts are gone. DM-50's deferred row can close |
| Notion | **Matches** `a2c6709`. One nit: A05's Work Register row predates OD-55 and this message |

**How to apply:** M1 to M17, X1 and X2 are in given words; line breaks may move. X2 applies only if Nathan chooses H (b).

## 3. Item 1.1 — The scope: keep P2 here

- **SV2's brief comes next** and needs to know whether a profile stores a home area. Moving P2 to SV3's brief would leave SV2 to guess, and a field added later is a schema change.
- **The third message comes before P07,** after SV2 to SV4.
- **P2 is the same kind of decision as P1:** who sees whom, under the same two-way rule. A05 owns both (the discovery fixtures, line 229; the reciprocal-eligibility fixtures, line 92).

## 4. Item 1.2 — The form

**Approved.**
- **Every item has the parts OD-32 asks for:** what it is, what breaks without it, the facts with their rows, the options, what each gains, and a recommendation with its basis.
- **"What this message is and is not" meets DM-37 4.3:**
  - the matrix's date and scope;
  - not legal advice;
  - no claim of compliance;
  - what the recommendations weigh and what they do not.
- **"Whether to take legal advice" meets 4.4:** it names the readings and takes no side.
- **L** is DM-38 section 8's optional line, as worded there.
- **The defaults without an answer** are DM-37 4.5's.

## 5. Item 1.3 — The recommendations

### P1 — approved; three facts made exact

- **(a), (x) and (m), with consent at entry, no sale and both declarations,** rest on the research's "minimize these fields" (section 6.4) and on consent from the start. Agreed.
- **The facts against their rows:**
  - only Google's form asks for data derived from other answers (GP-25; the matrix, section 9). Apple's row (AP-23) lists sexual orientation but has no derived-data rule;
  - California's row is a right to limit the use of sensitive data, not consent (UST-42). Only Virginia and Colorado require consent at their thresholds (UST-47, UST-48).
- **(m) hides less than it says.** Under the two-way rule, a viewer whose "show me" holds one value sees only members of that value. So that viewer knows the gender of everyone they are shown, whatever (m) hides. Nathan should know this before he chooses (m) for non-binary members' sake.

**M3:** replace `  - Own gender plus "show me" reveals sexual orientation. Both stores make Glow declare sexual orientation, including data derived from other answers (AP-23, GP-25).` with:

> ```
>   - Own gender plus "show me" reveals sexual orientation. Both stores make Glow declare sexual orientation (AP-23, GP-25), and Google also asks for data derived from other answers to be declared (GP-25).
> ```

**M4:** replace `  - Texas bars selling "sexuality" data without prior consent, even for a small business (UST-45). California, Virginia and Colorado require consent only above size thresholds Glow does not meet (UST-42, UST-47, UST-48).` with:

> ```
>   - Texas bars selling "sexuality" data without prior consent, even for a small business (UST-45). Virginia and Colorado require consent, and California gives a right to limit its use, only above size thresholds Glow does not meet (UST-47, UST-48, UST-42).
> ```

**M5:** replace `  - (m) lets a member keep their gender off the profile, which matters most to non-binary members; (n) shows every viewer the same facts.` with:

> ```
>   - (m) keeps a member's gender off their profile, which matters most to non-binary members, but not from a viewer whose "show me" holds one value: the two-way rule shows that viewer only members of that value. (n) shows every viewer the same facts.
> ```

### P2 — approved, with the location option the research names

- **Age (a)** follows P1's two-way rule. Agreed.
- **Location (a) cites the research but widens it.**
  - The research says "manually selected city/region", and asks for "privacy testing" of "repeated filter changes and tiny population groups".
  - The message offers "a city or ZIP code", and drops the testing.
  - The reason this matters: with a distance limit, and a home area a viewer can change, repeated searches can tell a viewer which area a member chose. That is safe only while the area is coarse, and a ZIP code is finer than the city wherever it is smaller.
- **The research's wording:** the message's "since repeated queries can narrow an approximate distance down to a place" is a paraphrase. The research's words are "exact distance values that enable triangulation".

**M2:** in the summary table, replace `| P2 | Do members filter by age and by place? | Whether a profile stores a home area; who appears in discovery | **An age range applied both ways; a typed home area with a distance limit, no distance shown** |` with:

> ```
> | P2 | Do members filter by age and by place? | Whether a profile stores a home area; who appears in discovery | **An age range applied both ways; a chosen home city or region with a distance limit, no distance shown** |
> ```

**M6:** replace `  - The original research recommends a manually chosen city or region, or coarse location while the app is open; never background location, exact coordinates or exact distances, since repeated queries can narrow an approximate distance down to a place.` with:

> ```
>   - The original research recommends a manually chosen city or region, or coarse location while the app is open; never background location, and never exact coordinates or exact distances, which enable triangulation. It also asks for privacy testing of repeated filter changes and of tiny population groups.
> ```

**M7:** replace `  - **Location:** (a) a home area the member types (a city or ZIP code), with a distance limit they set, measured between area centres, and no distance shown on profiles; (b) the device's coarse location while the app is open, with the same limit; (c) no location, so the pool is the whole US.` with:

> ```
>   - **Location:** (a) a home city or region the member chooses, with a distance limit they set, measured between area centres, and no distance shown on profiles; (b) the device's coarse location while the app is open, with the same limit; (c) no location, so the pool is the whole US.
> ```

**M8:** replace `  - Location (a) needs no location permission and reveals only an area. (b) follows a member who travels, but asks for permission and collects a sensitive data type. (c) collects nothing, but in a US-wide pool most people shown are far away.` with:

> ```
>   - Location (a) needs no location permission and reveals only the area the member chose; a ZIP code, which the research does not name, would reveal more wherever it is smaller than the city. (b) follows a member who travels, but asks for permission and collects a sensitive data type. (c) collects nothing, but in a US-wide pool most people shown are far away.
> ```

**M9:** replace `- **Recommendation: age (a) and location (a).** The basis: the same two-way rule as P1, and the least location data that still gives a nearby pool.` with:

> ```
> - **Recommendation: age (a) and location (a),** with SV3 testing what repeated filter changes and tiny population groups reveal, as the research asks. The basis: the same two-way rule as P1, and the least location data that still gives a nearby pool.
> ```

**M16:** in "Whether to take legal advice", replace `- whether a typed home area counts as precise geolocation (UST-42).` with:

> ```
> - whether a chosen city or region, or the device's coarse location, counts as precise geolocation (UST-42).
> ```

### R — approved; its reasoning corrected

- **Rematch needs no new data model.**
  - The message says that rematch added later "changes the data model's one-pair rule". The data model says the opposite: "One pair record; history/rematch requires policy, never a second match row for the same pair" (`Match`). The interactions fixtures say the same: "Preserve one pair identity".
  - So both resurfacing and rematch can be added later as policy changes on kept records. Rematch would need a new reviewed transition on the existing pair record.
  - (a) for both stands on simplicity and on keeping an unmatch final, not on how hard a later change would be.
- **"Never" depends on retention.** A pass or an unmatched pair stops blocking a return once its record is deleted. So "never" holds only while those records are kept, which ties R to the third message's retention.
- **The fraud-ban citation:** New York's notice (UST-08) binds only a paid service, and the matrix marks it "Not applicable now". The notices that bind now are Utah's, Vermont's, Arizona's and Colorado's (UST-14, UST-15, UST-17, UST-18).

**M10:** replace `- **What breaks without it:** SV3 builds the recorded defaults and says so. Pass records are kept either way, so resurfacing can be added later as a policy change. Rematch added later changes the data model's one-pair rule.` with:

> ```
> - **What breaks without it:** SV3 builds the recorded defaults and says so. Either can be added later as a policy change, with no new data model: each pass is a kept record, and a pair keeps one match record whatever happens to it (the data model). Rematch would need a new reviewed transition on that record.
> ```

**M11:** replace `  - Fraud-ban notices need a record of who received a banned member's messages, kept after an unmatch (USF-18 from 20 October 2027; UST-08, UST-14 and other states now). The record of a past match is therefore kept whatever you choose.` with:

> ```
>   - Fraud-ban notices need a record of who received a banned member's messages, kept after an unmatch (USF-18 from 20 October 2027; now in Utah, Vermont, Arizona and Colorado, UST-14, UST-15, UST-17 and UST-18; in New York only for a paid service, UST-08). The record of a past match is therefore kept whatever you choose.
> ```

**M12:** replace `- **Recommendation: (a) for both, at launch,** to revisit with real numbers. The cost: in a small pool, members reach "no more people" sooner.` with:

> ```
> - **Recommendation: (a) for both, at launch,** to revisit with real numbers. The cost: in a small pool, members reach "no more people" sooner. "Never" holds only while each pass and match record is kept, so the third message's retention needs to keep them for as long as both accounts exist.
> ```

### H — (b) approved as the recommendation; the manager's three points

**1. (b) changes the interim default.** Yes, and that is the point of asking.
- Today reads refuse whatever refuses a send (P06.2, "Stage C under OD-45"; D5).
- Under (b), SV4's brief gives reads their own rule. A read needs a valid session of an `active` reader and the match active with no block either way (OD-12). It no longer turns on either member's pause, restriction or consent.
- A suspended member cannot sign in, so only the other member reads.
- After a deletion the conversation is gone from view.

**2. Is (b) acceptable as the default on the security boundary? Yes:**
- the messages were already delivered, so hiding them later takes nothing back from the recipient;
- keeping them readable keeps the recipient's evidence for a report, and the context for a fraud-ban notice;
- a suspended member loses every route in. Sign-in is refused, the Stream user is deactivated and the tokens are revoked (D6, 5.1);
- removing a harmful message, or hiding a whole conversation, stays a moderation tool. It is P07's to design.

What (b) costs, and what the message must say:
- a member who withdraws consent, or is restricted or suspended, leaves their past messages readable to the other member until the account is deleted. Today's default hides them;
- "never why" has one exception: a fraud-ban notice must tell the recipient (USF-18 from 2027; four states now).

**3. Does (b) conflict with D6, or with the Standing guard?**
- **D6: no conflict in design, but one unproven dependency.**
  - D6 deactivates the Stream user on suspension, which ends that member's own access.
  - Stage C's reads are Glow's server-side reads by committed message IDs.
  - Whether Stream's server-side read still returns a deactivated user's messages is not shown anywhere: the history read's live row is still a prerequisite in the P11 plan. Under (b), that row must show it, which is X2.
- **The Standing guard: not triggered by (b).**
  - Under (b) no readable conversation loses a message.
  - Under the deletion rule the whole conversation leaves the other member's view.
  - The guard would apply later only if P07 removes a message from a readable conversation, and the P11 plan already says so (its policy-question bullet, "If the answer removes messages from a readable conversation…").

**On deletion:**
- AP-33 does settle that the other member keeps no readable copy of the deleted member's messages.
- It does not decide what happens to the other member's own messages. Removing the whole conversation, as an unmatch does, is Glow's rule, and a sound one, but it is a choice.
- After a deletion, AP-33 allows keeping only what the law requires. A safety report that no law requires is not enough.

**M13:** replace `  - **(b) Read-only for both:** both members keep reading the history; sending is refused; the conversation shows one neutral line, the same for every cause, such as "You can't send messages here right now".` with:

> ```
>   - **(b) Read-only for both:** both members keep reading the history (a suspended member cannot sign in, so there only the other member reads); sending is refused; the conversation shows one neutral line, the same for every cause, such as "You can't send messages here right now".
> ```

**M14:** replace `- **Account deletion, in every option:** Apple's rule leaves no option of a readable copy for the other member (AP-33). So a deletion works as an unmatch does under OD-12: the conversation leaves the other member's view, and its content is kept out of sight only where a safety report or the law requires it, for the period the third message sets.` with:

> ```
> - **Account deletion, in every option:** Apple's deletion covers content shared with others (AP-33), so the other member keeps no readable copy of the deleted member's messages. The rule for Glow: a deletion works as an unmatch does under OD-12. The conversation leaves the other member's view, and the deleted member's content is kept, out of sight, only where the law requires it (for example after a CyberTipline report, USF-04), for the period the third message sets.
> ```

**M15:** replace `  - (b) makes a pause cost nothing, and the other member learns only that messaging is stopped, never why.` with:

> ```
>   - (b) makes a pause cost nothing, and the other member learns only that messaging is stopped, never why, except where a fraud-ban notice must tell them (USF-18; UST-14, UST-15, UST-17, UST-18). Under (b), a member who withdraws consent, or is restricted or suspended, leaves their past messages readable to the other member until the account is deleted, so the consent screen must say so (G-10).
> ```

**X2 — only if Nathan chooses H (b):** in the P11 plan, at the end of the bullet "**The history read's live row**", add:

> Under H (b) of the second A05 message, the row also shows whether the read returns the messages of a user Stream has deactivated (P06.2's D6 deactivates on suspension); if it does not, reads of a suspended member's conversation need another route before P11 serves them.

### L — approved

DM-38 section 8's line, as worded there; OD-55 records English as the recommendation Nathan did not change.

### The opening, the header and the matrix

- **The opening:** it says "The facts are the matrix's", but P1 and P2 also rest on the original research, which is design advice, not the matrix.
- **The header:** the matrix's section 10 asks for a recheck "when Nathan … chooses … a preference taxonomy" and when "device location" is proposed. The message's routing does not include it.
- **The matrix:** section 9's sentence on the preference taxonomy blurs California's right to limit into "consent". That is how the error reached the message.

**M1:** replace `**What this message is and is not.** The facts are the matrix's, read from primary sources on 1 November 2026, for the US only (OD-55).` with:

> ```
> **What this message is and is not.** The legal and store facts are the matrix's, read from primary sources on 1 November 2026, for the US only (OD-55); the design advice is the original research's (23 September 2026).
> ```

**M17:** replace `- **Where the answer goes:** the owner-direction register (a new OD row); the carried-items file's SV2, SV3 and SV4 sections; A05's Work Register row.` with:

> ```
> - **Where the answer goes:** the owner-direction register (a new OD row); the carried-items file's SV2, SV3 and SV4 sections; A05's Work Register row; and the matrix's recheck of the rows a chosen preference taxonomy touches, and of device location's rows if P2's answer is (b) (the matrix, section 10).
> ```

**X1:** in the matrix, section 9, "The preference taxonomy", replace `consent is required at the thresholds, and in Texas before any sale even for a small business (UST-42, UST-45, UST-47, UST-48).` with:

> ```
> at the thresholds Virginia and Colorado require consent and California gives a right to limit its use; in Texas consent comes before any sale, even for a small business (UST-42, UST-45, UST-47, UST-48). [Corrected after DM-51: this said that consent is required at the thresholds in all four; UST-42's row is a right to limit.]
> ```

**Checked:** each passage that M1 to M17 and X1 replace appears exactly once in its file at `a2c6709`.

## 6. Item 2 — DM-50's conditions as applied

**Confirmed,** word for word at `c864edd` (`df8a04c` is in `main`):
- **1.1:** C2.5's reading, in the SV1 record.
- **1.2:** the carry, in "Carried to SV2".
- **2.1:**
  - the P11 plan's two new lines are present;
  - "the failed-sign-in rate limit;" is gone;
  - the "No reauthentication" line is gone.
- **2.2:** "revision 5" in the data model, the contract and the P11 plan, with no "revision 3" left in any of them. The brief is still at revision 5.
- **2.3:** the CI policy's counts-only words.

DM-50's deferred row can close.

## 7. Notion (read-only, at about 23:54 UTC; the pages as of 23:35 UTC)

What I read: the parts named here, not the whole of either large page.

- **Implementation Control:**
  - **The status** says the page was last matched at `a2c6709`, with its message.
  - **Main** is `c864edd`, with no PR open.
  - **The Branches bullet** lists three branches, matching my `git ls-remote` at 23:54 UTC: `main` (`c864edd`), the manager branch ("`a2c6709` at this sync") and `claude/dev-manager` (`85df720`). SV1's three session branches were deleted by cleanup run 42718647056.
- **The Dev Manager page:** both rows match the review log:
  - DM-50's row: answered at `85df720`, merged at `e3a768c`, every condition accepted at `df8a04c`;
  - DM-51's row: the consultation and the message at `a2c6709`, "Awaited".
- **The Work Register:**
  - **SV1** is Done, merged at `c864edd`, its evidence pinned at `578c0a6`.
  - **SV2** is Planned, with G-10 after Nathan's answer.
  - **A05, a nit:** its Next Action still reads "Resolve market/preference/retention/safety/support commitments when their owning feature or release requires them", and its Evidence link is P06.1's record. It does not mention OD-55's answers or this message. The message's routing already sends Nathan's answer there.
- The repository wins (OD-27).

## 8. Where each item goes

| Item | Goes to |
|---|---|
| M1 to M17 | The second A05 message, revision 2, before it goes to Nathan |
| X1 | The matrix, section 9, in the same commit |
| X2 | The P11 plan, only if Nathan chooses H (b), at the disposition of his answer |
| DM-50's conditions | The review log's deferred row closes |
| Reading the message as sent | My next consultation |

Status: complete
