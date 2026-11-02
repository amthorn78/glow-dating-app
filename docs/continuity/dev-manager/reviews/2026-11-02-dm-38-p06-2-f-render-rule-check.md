# DM-38 — P06.2-F: the render-rule check's design after C1's delta re-review

- **Consultation:** DM-38, revision 1, from App Manager 9, relayed by Nathan (OD-25).
- **Reviewer:** Dev Manager 3, `session_01KVuPEpFRh9B22beZKTKb27`, branch `claude/dev-manager`.
- **Date:** 2 November 2026.
- **Commit read:** `903c41f46aaae05f22574e4ad305ceae0a003a08` of `claude/magical-wozniak-yfmmx2`. **This read covers `903c41f`** (DM-03 G2).
  - The branch is now at `3cf2ee1`, which changes only the handoff and the mistakes log after `903c41f`.
  - `main` is `bac3c19`.
- **Environment (names only):** none of `DATABASE_URL`, `HD_API_KEY` or `GEO_API_KEY` is set, and no `STREAM_*` name is present.
- **What I did not do:** I called no provider, database, HDE, Railway or the TypeSafe API. I wrote nothing in the checkout except this report.
- **What I ran, all in a clean process environment:**
  - **The scratch copy:** `apps/mobile` and `packages` at `903c41f`, extracted by `git archive` outside the checkout, then `npm ci --ignore-scripts`.
  - **The test:** `display-rule.test.ts` passed 21 of 21.
  - **Probes:** each one an edit to the scratch `screen.tsx`, then the render test, `tsc --noEmit` and ESLint, then the file restored and its SHA-256 checked (`3aef02c3…`).
  - **Two throwaway changes** to the scratch copy of the test, to judge what a fix costs. I did not keep them, and the file is back to `903c41f`'s bytes.

## 1. What I read

- **The brief** (`docs/planning/p06-2-f-mobile-hardening.md`): all of it, including item 2, "Correction C1" and "Sessions".
- **The record:**
  - "Correction C1";
  - "Manager verification of correction C1";
  - "Delta re-review of correction C1", with its findings table.
- **The code:** `display-rule.test.ts`, all of it; `screen.tsx`; `rows.ts`.
- **Process:**
  - the manager workflow's step 6, including "Fix or carry, by rule" and the delta re-review rule;
  - the review log's "Deferred conditions";
  - AM8-21 to AM9-03 in the mistakes log.
- **For item 5:**
  - PF01 at `903c41f` against `fcd6ebc`;
  - the first A05 message as sent (`docs/ephemeral/2026-11-01-a05-first-decision-message.md`);
  - OD-55 and OD-56;
  - the carried-items file's SV4, P08 and P06.3 sections.
- **Notion, read-only:** *Implementation Control*'s status section (as section 9 says); the Work Register row P06.2-F; the uses table's P06.2-F rows.

## 2. Verdicts

| Item | Verdict |
|---|---|
| 1 The disposition | **Approved, with one precision:** C2 fixes findings 2 to 5. Finding 1 is not fixed; it is settled by the narrowed claim this report approves. Nits 6 and 8 ride along; nit 7 stays a recorded limit (section 5) |
| 2 The fix's design | **Approved with conditions 2.1 to 2.6:** option (b), plus closing finding 2's class, which my probe shows is small. Finding 1's class stays a named limit, described as what it is. Option (c) is carried to the next change to how the chat screens hold their data (section 4) |
| 3 The brief | **Approved.** No read is needed before C2's prompt runs if revision 2 states section 4's guarantee and limits |
| 4 The manager's share | **Approved with conditions 4.1 and 4.2:** the prevention is right but too weak on two points |
| 5 The deferred reads | **DM-37 2.7 confirmed word for word. DM-37 4.1 to 4.4 met,** and 4.5 was taken. Two notes (section 8) |
| 6 Notion | **Matches `903c41f`** in what I read (section 9) |

## 3. What I tried

**Forms of my own,** each an edit to `screen.tsx`:

| # | Form | Render test at `903c41f` | `tsc` / ESLint |
|---|---|---|---|
| F0 | **A harmless `FlatList`:** `<FlatList data={conversation.messages} keyExtractor={entry => entry.submission_id} renderItem={({ item }) => <Text>{item.text ?? ''}</Text>} />` | **Fails:** `a widening to Readonly<ArrayLike<ConversationMessage>> \| undefined: conversation.messages`. A false positive | pass / pass |
| F1 | **F0's list with a loosely typed `renderItem`** (`({ item }: { item: { name?: string; text: string \| null } })`), rendering `item.name` | Fails, but only by F0's rule on `data` | pass / pass |
| F2 | **A render function passed by reference:** `function renderEntry(entry: { name?: string; text: string \| null })` rendering `entry.name`, used as `{conversation.messages.map(renderEntry)}` | **Passes** | pass / pass |
| F3 | **Grouped sections:** `const sections = [{ title: 'Today', data: conversation.messages }]`, rendered by a `Day` helper whose loosely typed `data` renders `entry.name` | **Passes** | pass / pass |
| F4 | **The review's `shout`:** `[message].map(shout)` | Passes | pass / pass |
| F5 | **A `useCallback` render function** with a loose parameter, used as `.map(renderRow)` | Passes | pass / pass |
| F6 | **An object's method by reference:** `conversation.messages.map(view.line)` | Passes | pass / pass |

**Two throwaway changes to the test:**
- **Compare a function passed by reference** against what the caller passes, as the inline-callback check already does.
  - **Size:** about twelve lines.
  - **Result:** all 21 tests passed: today's two files, and the 22 planted forms with their named reasons. F2, F4, F5 and F6 then failed with the new refusal.
- **Follow Glow's data into properties and type arguments.**
  - **Result:** it failed today's harmless code, with `a widening to ChatStore: store` at `useViewedMessages(store, …)`.
  - **What it would take:** reworking `keeps` (identical types, index signatures, and a depth cut-off that passes everything beyond it). That is option (a)'s cost, as the manager estimated.

## 4. Item 2 — the fix's design

**Option (b) is adequate as a second layer for the screens as they are, with the conditions below.** It is not adequate for the next change to how those screens hold their data; 2.5 covers that change.

**Why it is adequate today:**
- the validator, with its 15 provider-field cases, is the first guard, and the screens are typed against the contracts;
- no real data flows at fixture scope;
- today's screen uses no wrapper, no function passed by reference and no list component.

**One premise of (b) does not hold:** "the test catches an accidental read of a field, not a deliberate evasion". F2 and F3 are ordinary refactors (a render function, grouped sections), not evasions.

**Conditions:**
- **2.1 C2 closes finding 2's class.**
  - A function passed by reference is compared against what the caller passes, as an inline callback is.
  - The planted forms include the review's `shout`, a render function, a `useCallback` function and a method.
  - **The stop rule:** if this cannot pass today's two files without a new exception, the session stops and reports. No exception is added without the Dev Manager.
- **2.2 The type-guard refusal works by signature, not by where the guard is declared.** It refuses:
  - a call whose resolved signature has a type predicate or an assertion, except the default library's;
  - such a signature declared in the two files.

  A guard imported from another module narrows the data in the same way, which is why the refusal works by signature.
- **2.3 Finding 1's class stays a named limit, described as what it is:** data held inside another value. That includes groups or sections, a list component's render-item wrapper, a view-model object, a closure and a container. The test comment, the record and the brief say that an ordinary refactor reaches it.
- **2.4 The false positive is recorded:** a harmless `FlatList` over Glow's data fails today (F0), because `ArrayLike` has an index signature.
  - It fails closed, which is safe.
  - It is recorded so that the next author changes the design (2.5) and does not loosen the check by hand.
- **2.5 Option (c) is carried to the next change to how `screen.tsx` or `rows.ts` hold or render chat data, not to P06.3 by name.**
  - **That change** might be a list component, grouping, or a helper or control that takes messages, for example P07.2's report from chat. P06.3 is notifications, and its carried items name no chat screen.
  - **What that change does:**
    - it builds view models by explicit field copy, as `rows.ts` does;
    - its check becomes "no contract type reaches the screen", with planted forms;
    - it gets a full exact-head review.
  - Its brief may propose another design to the Dev Manager.
- **2.6 The rest of (b) stands as the manager wrote it:**
  - the narrowed guarantee, with 2.1 to 2.4 applied;
  - `Reflect`, and `Object` members other than `freeze`, refused by identifier however aliased;
  - both exceptions narrowed to their words;
  - the `GLOW_DATA` check (nit 6);
  - the Mobile row (nit 8);
  - one planted form per closed class.

**The guarantee,** for the test comment, the record and the brief (item 3):

> The check follows Glow's data by its own type: at a property read, a destructuring, a spread, an enumeration and an `in` check, and wherever the data is passed, returned, assigned, annotated, given as a prop, or given to a callback, inline or by reference. It refuses type predicates and assertion signatures, references to `Reflect` and to `Object` members other than `freeze` however aliased, and any type error. It does not follow data held inside another value (a group or section, a list's render-item wrapper, a view-model object, a closure or a container), another module, or a template literal's coercion. It refuses some harmless code, such as a list component over Glow's data. It is a test over two files' source, not a proof over all programs.

**The other options:**
- **(a):** section 3 shows a first step already fails harmless code.
- **(c) now:** a runtime change, outside C2's stop rule, needing a full review.
- **(d):** rule (a) does not allow it.

## 5. Item 1 — the disposition

**Agreed, with one precision:**
- **C2 fixes findings 2 to 5:**
  - **finding 2** by 2.1;
  - **finding 3** by 2.2 and the refusal by identifier;
  - **finding 4** by the narrowed exceptions;
  - **finding 5** by a claim that is true.
- **Finding 1 is not fixed.** The narrowed claim and 2.5 settle it.
  - Step 6 consults the Dev Manager "when the rule does not decide", and this read decides it.
  - The review log records it that way.
- **The nits:** 6 and 8 ride along. Nit 7 stays a recorded limit, since it fails closed.
- **The re-review:** C2 changes no non-test line, so it gets a delta re-review (step 6). Its prompt holds the reviewer to the guarantee:
  - a form inside a named limit is not a finding;
  - a form outside every limit is a finding;
  - the reviewer tries forms of its own against each mechanism the guarantee names.

## 6. Item 3 — the brief

- **Agreed.** Revision 2 restates Outcome 1 of "Correction C1" as section 4's guarantee and limits, and C2's Outcome lists 2.1 to 2.6.
- **No read is needed before C2's prompt runs, if revision 2 uses this report's terms:**
  - the brief is not governing Markdown;
  - its own Dev Manager terms ask no read for applying a verdict.

  My next consultation confirms it.

## 7. Item 4 — the manager's share (AM9-03)

**The prevention points the right way, but it is not enough on two points:**
- **4.1 Trying forms does not license the claim.**
  - After trying forms of its own, the manager still attributes a completeness claim to the session, with its own forms and their results beside it.
  - No test over source proves "through any binding", so the manager never makes such a claim in its own words.
  - AM9-03's "either … or" becomes "and".
- **4.2 Part of the cause is the brief.**
  - C1's Outcome 1 asked for a check that "fails … through any binding", which no source check can show. The session then claimed exactly that.
  - **The rule:** a brief asks for named forms and a stated guarantee with its limits. It never asks for "any" or "every" over arbitrary code.
  - This goes into AM9-03's prevention, or into an entry of its own, as part of the manager's own share.

## 8. Item 5 — the deferred reads

- **DM-37 2.7 is confirmed:**
  - the sentence is in PF01 §7 word for word, once, right after "Recheck official policies and build requirements when producing release artifacts.";
  - nothing else in that paragraph changed;
  - the 1.17 entry cites DM-37 2.7.
- **DM-37 4.1 to 4.4 are met:**
  - **D1** asks where the business is established and who holds the accounts.
  - **D2** shows:
    - every option, each with its rows, named people, representatives, clocks and "not priced yet";
    - the US option as one set (AP-64);
    - the basis of the recommendation, and what it does not weigh.
  - **D3** links age assurance to geography: UK-12 to UK-14 and UK-35; UST-37 and UST-38; EU-24 and EU-25.
  - **The legal-advice paragraph** names exactly 4.4's rows and takes no side.
  - **4.5** was taken.
- **OD-55 reads Nathan's answers rightly. Two notes:**
  - **English** is recorded as the recommendation he did not change, not as his own answer. Optional: the second A05 message confirms it in one line.
  - **One follow-up reply overstates a DPIA point.** It said a DPIA is needed "since orientation data, matching and age checks are high-risk".
    - The matrix leaves that to the DPIA tests ("likely high risk", "large scale": EU-25, EU-46, EU-47).
    - No decision rested on it, since Nathan chose the US only.
    - At an EU launch, the DPIA question is read from those rows, not from that sentence.
- **The Deferred rows** DM-37 2.7 and DM-37 4.1 to 4.4 are done.
- **Under OD-55:**
  - G-12 is carried, conditional, to an EU launch, as DM-37 2.3 asks;
  - G-09 is carried likewise, to a UK or EU launch.

## 9. Notion

- ***Implementation Control*:**
  - **What I read:**
    - the status section's lead: its matched commit `903c41f`, and the entries back to `cdc7c48`;
    - in full, its standing bullets Phase, Next items, Dev Manager, Manager, Main and Branches;
    - the opening of the Mistakes log bullet, which lists AM9-01 to AM9-03.

    These match `903c41f`.
  - **The branch list** matches `git ls-remote`. The manager branch has since moved to `3cf2ee1`, Markdown only.
  - **What I did not read:** the rest of the 161,000-character section, which is history, including the rest of the Mistakes log bullet.
- **P06.2-F's Work Register row** matches `903c41f`, including AM9-03's correction.
- **The uses table's row "P06.2-F C1 delta re-review"** matches the brief: a review, v8.2, the same TypeSafe cell the brief records, *Nathan's pick* "not recorded", and PR40 at `0881db5`.

## 10. Where each item goes

- **C2's prompt:** 2.1 to 2.6, with section 4's guarantee.
- **The brief, revision 2:** section 4's guarantee and limits (item 3).
- **The carried-items file:** 2.5, under the next change to how the chat screens hold their data.
- **The delta re-review's prompt:** section 5's standard.
- **The mistakes log:** 4.1 and 4.2.
- **The review log:**
  - DM-38's disposition;
  - DM-37 2.7 and 4.1 to 4.4 marked done;
  - a Deferred row for 2.5.

Status: complete
