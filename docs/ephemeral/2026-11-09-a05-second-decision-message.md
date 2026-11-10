# The second A05 decision message — who sees whom, resurfacing and rematch, chat history while messaging is stopped

- **Owner:** App Manager 10. Sent to Nathan in the manager session on 10 November 2026, as written below, after DM-51 ([report](../continuity/dev-manager/reviews/2026-11-09-dm-51-a05-second-message.md), answered at `0fc2426`, a read of `a2c6709`) approved it with conditions M1 to M17, applied as written; the Dev Manager's next consultation reads it as sent.
- **Revision 2, 10 November 2026:** DM-51's M1 to M17, as written, and M3's finding applied once more, in the legal-advice paragraph ("Google asks", where revision 1 said "the stores ask"). Revision 1 (9 November) was the text DM-51 read.
- **Why:** OD-50 sends the open A05 questions to Nathan in OD-32's form, through the Dev Manager first (the matrix, section 9). DM-37 4.5 put the preference taxonomy, resurfacing and rematch, and the history policy in this message, before SV2's brief; DM-38 section 8 adds a one-line confirmation of the language. P2 (age range and location) is also A05's (the discovery and reciprocal-eligibility fixtures, "A05 owns … age ranges, distance"), and no message has scheduled it. The matrix is [`docs/planning/store-legal-safety-requirements.md`](../planning/store-legal-safety-requirements.md); row IDs below are its rows.
- **Where the answer goes:** the owner-direction register (a new OD row); the carried-items file's SV2, SV3 and SV4 sections; A05's Work Register row; and the matrix's recheck of the rows a chosen preference taxonomy touches, and of device location's rows if P2's answer is (b) (the matrix, section 10).
- **Deletion condition:** prune after Nathan's answer is in the register and the Dev Manager's next consultation has read this message as sent.

---

**Four decisions before the profiles slice (SV2), and one confirmation.** Nothing breaks today: Glow has no users, and the release block stands. SV2's brief needs P1 and P2 (what a profile stores, and the consent screen), SV3's needs P2 and R, and SV4's needs H. Without an answer, each brief keeps the recorded default and says so.

| # | Question | What it changes | Recommendation |
|---|---|---|---|
| P1 | What does a member say about their gender, and whom do they want to see? | The fields that decide who sees whom; a consent step | **Woman, man or non-binary; "show me" any combination; no separate orientation field; the member chooses whether their gender shows** |
| P2 | Do members filter by age and by place? | Whether a profile stores a home area; who appears in discovery | **An age range applied both ways; a chosen home city or region with a distance limit, no distance shown** |
| R | Can a passed profile come back, and can two people who unmatched match again? | SV3's interaction rules | **Neither, at launch** |
| H | What can each member read while messaging is stopped by a pause, a restriction, a suspension or a withdrawn consent? | SV4's history reads | **Read-only for both, with one neutral line for every cause** |
| L | Is English the only language at launch? | Recorded as your answer | **Yes** |

**What this message is and is not.** The legal and store facts are the matrix's, read from primary sources on 1 November 2026, for the US only (OD-55); the design advice is the original research's (23 September 2026). It is not legal advice, it does not show that Glow is or would be compliant, and nothing here has a cost. The recommendations weigh what one operator (you, OD-23) must run and how little sensitive data Glow holds. They do not weigh your audience or your business reasons, and those can outweigh them.

## P1 — Gender, and whom each member wants to see

- **What it is:** the fields that decide who sees whom. The rule is already built: two people see each other only if each one's own value is among the values the other chose (P05.1). Today the fields hold placeholders ("Demo option A" and "B").
- **What breaks without it:** SV2 cannot fix the stored fields or the consent step (gap G-10). Without an answer, SV2 builds the versioned catalog with the placeholders, and the launch values wait for your answer before launch.
- **The facts:**
  - Own gender plus "show me" reveals sexual orientation. Both stores make Glow declare sexual orientation (AP-23, GP-25), and Google also asks for data derived from other answers to be declared (GP-25).
  - Texas bars selling "sexuality" data without prior consent, even for a small business (UST-45). Virginia and Colorado require consent, and California gives a right to limit its use, only above size thresholds Glow does not meet (UST-47, UST-48, UST-42).
  - FTC guidance asks for affirmative consent before collecting sensitive data (USF-13; guidance, not binding).
- **Options:**
  - **Own gender:** (a) woman, man, non-binary; (b) woman, man; (c) a longer list, or the member's own words.
  - **Whom they want to see:** any combination of the same values, in every option.
  - **Orientation as its own field:** (x) not asked; (y) an optional profile field.
  - **Whether own gender shows on the profile:** (m) the member chooses; (n) always shown. "Show me" is never shown, as today.
- **What each gains:**
  - (a) includes non-binary members with a short list the two-way rule handles; (b) is the simplest, but leaves non-binary people out; (c) describes more people, but the member's own words cannot drive a two-way rule without a mapping, and each extra value splits a small launch pool.
  - (x) collects nothing the matching rule needs; (y) lets members say more about themselves, at the cost of a second sensitive field.
  - (m) keeps a member's gender off their profile, which matters most to non-binary members, but not from a viewer whose "show me" holds one value: the two-way rule shows that viewer only members of that value. (n) shows every viewer the same facts.
- **Recommendation: (a), (x) and (m),** with consent asked at the step where these are entered, the data never sold, and both stores' declarations made. The basis: the smallest set of sensitive data the two-way rule needs (the original research: "minimize these fields"), and consent from the start, so nothing changes if Glow grows past the thresholds.

## P2 — Age range and location

- **What it is:** two more filters that A05 owns: the ages a member wants to see, and how near. Neither exists today, so discovery draws on the whole pool.
- **What breaks without it:** SV2 cannot fix whether a profile stores a home area, and SV3 cannot filter by age or place. Without an answer, there is no age or place filter, and the pool is the whole US.
- **The facts:**
  - Precise geolocation is sensitive personal information under California's law, above its threshold (UST-42). Both stores make Glow declare location, coarse or precise (AP-23, GP-25).
  - The original research recommends a manually chosen city or region, or coarse location while the app is open; never background location, and never exact coordinates or exact distances, which enable triangulation. It also asks for privacy testing of repeated filter changes and of tiny population groups.
- **Options:**
  - **Age range:** (a) each member sets a range, applied both ways (each must fall within the other's range), from 18 with no upper limit until set; (b) the viewer's range only; (c) no age filter.
  - **Location:** (a) a home city or region the member chooses, with a distance limit they set, measured between area centres, and no distance shown on profiles; (b) the device's coarse location while the app is open, with the same limit; (c) no location, so the pool is the whole US.
- **What each gains:**
  - Age (a) matches P1's two-way rule: no one sees a person who would not want to see them. (b) shows a viewer more people, including some outside those people's own range. (c) is the simplest.
  - Location (a) needs no location permission and reveals only the area the member chose; a ZIP code, which the research does not name, would reveal more wherever it is smaller than the city. (b) follows a member who travels, but asks for permission and collects a sensitive data type. (c) collects nothing, but in a US-wide pool most people shown are far away.
- **Recommendation: age (a) and location (a),** with SV3 testing what repeated filter changes and tiny population groups reveal, as the research asks. The basis: the same two-way rule as P1, and the least location data that still gives a nearby pool.

## R — Resurfacing and rematch

- **What it is:** whether a profile a member passed on can appear to them again, and whether two people who unmatched can become a match again.
- **Today:** neither (the interactions fixtures), with one pair record for any two people (the data model).
- **What breaks without it:** SV3 builds the recorded defaults and says so. Either can be added later as a policy change, with no new data model: each pass is a kept record, and a pair keeps one match record whatever happens to it (the data model). Rematch would need a new reviewed transition on that record.
- **The facts:**
  - No store rule covers either; blocking is required (AP-05, GP-06).
  - Fraud-ban notices need a record of who received a banned member's messages, kept after an unmatch (USF-18 from 20 October 2027; now in Utah, Vermont, Arizona and Colorado, UST-14, UST-15, UST-17 and UST-18; in New York only for a paid service, UST-08). The record of a past match is therefore kept whatever you choose.
  - Colorado's annual report asks how removed members are kept from re-registering (UST-20).
- **Options:**
  - **Resurfacing:** (a) never, so a pass is final; (b) passed profiles return after a waiting period you name; (c) an undo of the last pass only, straight after it.
  - **Rematch:** (a) never; (b) only if both like each other again after a waiting period, and never after a block or a report.
- **What each gains:**
  - Resurfacing (a) is the simplest, and respects a pass. (b) gives a small launch pool a second look. (c) fixes a mistaken swipe at once, with no lasting change.
  - Rematch (a) keeps an unmatch final, so it cannot be used to reach someone again. (b) lets two people repair a mistaken unmatch.
- **Recommendation: (a) for both, at launch,** to revisit with real numbers. The cost: in a small pool, members reach "no more people" sooner. "Never" holds only while each pass and match record is kept, so the third message's retention needs to keep them for as long as both accounts exist.

## H — Chat history while messaging is stopped

- **What it is:** what each member can read when messaging stops for a reason other than an unmatch or a block: either member pauses their profile, moderation restricts a profile, an account is suspended, or a member withdraws consent. And what the other member sees when an account is deleted.
- **Decided already** (OD-12): after an unmatch or a block, neither person can send or see the conversation, and the history is kept out of sight only for safety reports.
- **Today, the interim default:** reads refuse whatever refuses a send (the P06.2 brief, D5; the P11 plan). In each case above, the conversation disappears for both members. The paused member loses their own conversations, and the other member sees it vanish, as if they had been unmatched.
- **What breaks without it:** SV4 builds the interim default and says so.
- **The facts:** a CyberTipline report requires the reported content to be kept for one year (USF-04). Apple's account deletion covers content shared with others, keeping only what the law requires (AP-33); Google's covers the data declared in Data safety (GP-33).
- **Options:**
  - **(a) Keep today's default:** the conversation is hidden from both while messaging is stopped, and returns when it resumes.
  - **(b) Read-only for both:** both members keep reading the history (a suspended member cannot sign in, so there only the other member reads); sending is refused; the conversation shows one neutral line, the same for every cause, such as "You can't send messages here right now".
  - **(c) (b) for a member's own pause only, and (a) for every other cause.**
- **Account deletion, in every option:** Apple's deletion covers content shared with others (AP-33), so the other member keeps no readable copy of the deleted member's messages. The rule for Glow: a deletion works as an unmatch does under OD-12. The conversation leaves the other member's view, and the deleted member's content is kept, out of sight, only where the law requires it (for example after a CyberTipline report, USF-04), for the period the third message sets.
- **What each gains:**
  - (a) is one rule, and nothing is readable while contact is refused. But a pause costs a member their conversations, and the other member sees what looks like an unmatch.
  - (b) makes a pause cost nothing, and the other member learns only that messaging is stopped, never why, except where a fraud-ban notice must tell them (USF-18; UST-14, UST-15, UST-17, UST-18). Under (b), a member who withdraws consent, or is restricted or suspended, leaves their past messages readable to the other member until the account is deleted, so the consent screen must say so (G-10).
  - (c) keeps a member's own history through their pause, and hides it whenever moderation or the other member is the cause.
- **Recommendation: (b).** The basis: no message leaves a readable conversation, and a pause stays distinct from a rejection. A safety case that needs more, such as hiding a conversation, is P07's to design with your answer to the third message.

## L — The language

OD-55 records English as my recommendation, which you did not change, not as your answer. **Confirm English as the only language at launch,** and I record it as yours.

## Whether to take legal advice

That is your decision (DM-31), and this message takes no side. The decisions above touch readings the sources leave to interpretation:
- whether own gender plus "show me" is "sexual orientation" or "sexuality" data under the state laws (UST-45, UST-47, UST-48); Google asks Glow to declare derived data either way (GP-25);
- whether a chosen city or region, or the device's coarse location, counts as precise geolocation (UST-42).

**The rest of A05 comes later,** in a third message before P07's brief: retention, and who moderates and how fast.

**DECISION NEEDED:** your answers to P1 (gender (a) to (c); orientation (x) or (y); display (m) or (n)), P2 (age (a) to (c); location (a) to (c)), R (resurfacing (a) to (c); rematch (a) or (b)), H ((a) to (c)) and L (yes or no). A reply like "P1: a, x, m; P2: a, a; R: a, a; H: b; L: yes" is enough, or "accept your recommendations".

---

## Follow-up (10 November 2026)

**Nathan's answer:** "I want the options that are the most flexible, progressive, and configurable, and I need to be able to easily update these things in the admin console"

**The manager's reply, as sent:**

**My reading of your answer: every choice becomes a setting you can change in the admin console. Each starts at the default below, and a few fixed limits are ones the console cannot cross.** The console is the WordPress staff plugin, which P07 builds. It changes settings only through scoped Django APIs (PF01 §1, OD-19).

| Item | What you can change in the console | Launch default | Fixed limit, and why |
|---|---|---|---|
| P1 gender | The gender list (add, rename or retire values); members may also describe themselves in their own words, shown only if they choose | Woman, man, non-binary | Matching uses a list value; free words cannot drive the two-way rule |
| P1 "show me" | Follows the list: any combination | Any combination | — |
| P1 orientation | An optional field, with its own list and the member's own words; turn it off or on | On, optional, shown only if the member chooses | Never used for matching |
| P1 display | Each member chooses whether each field shows | Gender and orientation hidden until the member shows them | "Show me" is never shown |
| P2 age | The default range, and whether it applies both ways or only to the viewer | Both ways, 18 and up | Never below 18 |
| P2 location | The distance choices and their default. Each member picks a city or region, or the phone's approximate location while the app is open | Both ways of locating offered | No exact coordinates and no exact distance shown, ever (the research: they enable triangulation) |
| R resurfacing | On or off, the waiting period, and an undo of the last pass | Off; undo off | — |
| R rematch | On or off, and the waiting period | Off | Never after a block or a report |
| H history | For each cause (own pause, the other member's pause, restriction, suspension, withdrawn consent): hidden or read-only | Read-only for every cause | Unmatch and block stay hidden (OD-12); deletion follows Apple's rule (AP-33); a change that makes more readable reaches a member only after they accept updated consent wording (G-10) |
| L language | Not a console setting: adding a language means translating and reviewing every screen and legal notice, so it ships as an app release | English, with the app's text kept ready for translation | — |

**For every setting:**
- each change is versioned and audited: who changed it, when, and the old and new value;
- it applies from then on, and discovery refreshes;
- a setting that collects a new kind of data (orientation, the phone's location) needs the app's permission wording and both stores' privacy declarations in place before it can be switched on, so the first release declares them.

**What it changes in the plan:**
- SV2 to SV4 build each setting as a stored, versioned record with its launch default, instead of a fixed rule;
- P07's console gets their edit screens;
- there is more test work, since each setting value needs its own tests, but no money cost.

The design goes to the Dev Manager with SV2's brief, as every brief does. The fixed limits above are my recommendation, and the Dev Manager reads them there.

**DECISION NEEDED:** is this your answer? A "yes" records it as an owner direction with these launch defaults. Otherwise, name what to change; for example, a default you want switched on at launch.

**Nathan:** "orientation DOES need to be used for matching"

**The manager's reply, as sent:**

**Then orientation matches the way gender does: both ways.** Each member states their orientation and chooses which orientations they want to see. Two people see each other only if each one's orientation is among those the other chose, as well as each one's gender. The rule Glow already has handles more than one such field (P05.1), so this adds a second field, not a new mechanism.

The P1 orientation row becomes:

| Item | What you can change in the console | Launch default | Fixed limit, and why |
|---|---|---|---|
| P1 orientation | The orientation list (add, rename or retire values); whether members can narrow by it; the member's own words, for display only | Optional to state. "Orientations I want to see" starts at all of them, so narrowing is the member's choice. Shown on the profile only if the member chooses | Matching uses a list value, both ways. A member who states none appears only to viewers who keep all orientations |

**What this means:**
- **Hiding protects less.** As with gender, a viewer who narrows to one orientation knows the orientation of everyone they are shown, whether or not those members show it on their profile.
- **The data is now collected directly and used for matching.** It is still the same sensitive category: consent at the step where it is entered, never sold (UST-45), and declared in both stores (AP-23, GP-25), as already planned.

**DECISION NEEDED:** is the table, with this row, your answer? A "yes" records it as an owner direction with these launch defaults. Otherwise, name what to change.

**Nathan (while the reply above was being recorded):** "also, what about relationship status and looking for?"

**The manager's reply, as sent:**

**Neither is decided yet.** The original research lists "dating intent" for onboarding and nothing more, and no relationship status has been recorded. Both fit the same pattern as gender and orientation, so two more rows join the table:

| Item | What you can change in the console | Launch default | Fixed limit, and why |
|---|---|---|---|
| P1 looking for | The list; whether members can narrow by it | A proposed starting list: a long-term relationship; something short-term; something casual; new friends; still figuring it out. A member picks one or more, and "show me people looking for" starts at all, so narrowing is the member's choice. Shown on the profile | Matching uses list values, both ways |
| P1 relationship status | The list; whether members can narrow by it | A proposed starting list: single; separated or divorcing; partnered, in an open or non-monogamous relationship. A member picks one, and "show me" starts at all. Shown only if the member chooses | Matching uses list values, both ways |

**What this means:**
- **Each field a member narrows shrinks who they see,** and in a small launch pool that can leave few people. That is why every "show me" starts at all.
- **The starting lists are my proposal.** You can edit them in the console before launch or at any time.
- **Relationship status may count as information about a person's "sex life",** which two of the state laws treat as sensitive (UST-42, UST-48). It gets the same handling as orientation: consent at entry, never sold, and declared in both stores. The matrix's recheck of the rows this taxonomy touches covers it (section 10).

**DECISION NEEDED:** is the table, with the orientation row and these two rows, your answer? A "yes" records it as an owner direction with these launch defaults. Otherwise, name what to change.

**Nathan:** "yes"

**Recorded** as OD-60: every item a setting editable in the admin console, at the launch defaults and within the fixed limits above; orientation matched both ways; looking for and relationship status added as two-way list fields; English as his answer.
