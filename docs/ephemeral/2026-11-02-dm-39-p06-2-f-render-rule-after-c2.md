# DM-39 consultation — P06.2-F: the render-rule check after C2's own probes

- **Owner:** App Manager 9. Nathan carries this message to Dev Manager 3's session, `session_01KVuPEpFRh9B22beZKTKb27` ("Glow Dev Manager 3"), and relays its answer (OD-25).
- **Revision 1, 2 November 2026.**
- **Why:** correction C2 met its Outcomes, but its own probes found 49 forms in nine classes that pass the check and fall outside every limit DM-38 section 4's guarantee names. Under DM-38, a change of design, or a new exception, goes to the Dev Manager first, and the delta re-review's standard (a form outside every limit is a finding) would turn these into findings at once.
- **Where the result goes:** your report in `docs/continuity/dev-manager/reviews/`; the manager's disposition in the [review log](../continuity/dev-manager/README.md), "DM-39"; the P06.2-F brief's next correction or its review prompt.
- **Stream variables:** none are needed.
- **If no report arrives:** P06.2-F stays unmerged and no prompt is written; the manager asks Nathan whether the session is still available.
- **Deletion condition:** prune after the review log holds DM-39's disposition and PR40's merge receipt is recorded.

**Manager:** before giving this message to Nathan, replace every `<RECORDS_COMMIT>` with the full SHA of the manager-branch commit that holds this revision.

---

**DM-39 — P06.2-F: the render-rule check after C2's own probes.** From App Manager 9, relayed by Nathan. This consultation is revision 1, at commit `<RECORDS_COMMIT>` of `claude/magical-wozniak-yfmmx2`.

Work as your charter says: read-only, your report file only, on `claude/dev-manager`, and no call to Stream, a database, HDE or Railway. Check environment variable names only. You may run the mobile unit tests in a clean process environment in a scratch copy outside the checkout.

**Where it stands.**
- **Correction C2** (branch `claude/inspiring-ramanujan-tjpril`, code head `816cd60`; one test file, +222 −39 against `0881db5`; no runtime line) applied DM-38's 2.1 to 2.6:
  - a function passed by reference is compared against what the caller passes, return included;
  - type predicates and assertions are refused by signature, imported ones included;
  - `Reflect` and `Object` members are refused by identifier, type and key;
  - the two exceptions are narrowed to their words;
  - `GLOW_DATA` is checked;
  - the test comment states section 4's guarantee, with the `FlatList` false positive planted to fail closed;
  - 16 new planted forms, each with its reversal.

  Its run of record (41513359474) passed all eight jobs. The manager verified it and merged it at `880a42f` (the record, "Manager verification of correction C2").
- **C2's own probes** (the record, "Correction C2"): seven probe agents tried 256 forms, and a verifier re-ran each that passed. At `816cd60`, **49 forms in nine classes pass the test, `tsc` and ESLint, outside every named limit:**
  - **N1, narrow then widen (20 forms):** data given a subset type of its own declaring, then widened. One of them, X2, is an intermediate component with a narrower prop, an ordinary refactor;
  - **N2, a suppressed type error (7);**
  - **N3, Glow's data as `this` through `.call` (8),** for example `({}).hasOwnProperty.call(message, 'name')`;
  - **N4, a tuple's later elements, or arrays four deep (5).** The verifier contests this one, reading it as the container limit;
  - **N5, a thrown value caught as `any` (2);**
  - **N6, `for…of` into an existing variable (3);**
  - **N7, `arguments[0]` (3);**
  - **N8, an inline parameter typed only by its default (1);**
  - **N9, `instanceof` narrowing (2),** counted within N1.

  The session also wrote a scratch candidate, not committed. It refuses a narrowing to a non-Glow type, any `@ts-` directive, and `this` with no declared parameter. It passes today's files and every planted form, and closes 36 of the 49. But it refuses five harmless controls, such as a narrow `{ text }` prop that reads only `.text`.
- **The manager's re-run:**
  - N1 (a `Narrow` component passing to a `Wide` one) and N3 passed the test, `tsc` and ESLint;
  - its own N2 variant (`@ts-expect-error` above `{message.name}`) was caught by the source check and ESLint;
  - the session's seven N2 forms were not re-run.
- **The pattern:** three rounds have each found forms outside the stated claim: C1's exact-head review, its delta re-review, and C2's own probes. A source check over arbitrary TypeScript is not converging on its guarantee.
- **What else guards the display rule, as in DM-38:**
  - the client validator, which refuses a provider-shaped field;
  - the screens' contract types;
  - fixture scope;
  - DM-38 2.5's design change (view models), carried to the next change to how the chat screens hold their data.

**Read, at `<RECORDS_COMMIT>`:**
- the record's "Correction C2" and "Manager verification of correction C2" (`docs/testing/evidence/2026-11-01-p06-2-f-mobile-hardening.md`);
- `apps/mobile/src/chat/display-rule.test.ts` at `816cd60`;
- your DM-38 report, sections 4 and 5;
- the brief's "Correction C2" (`docs/planning/p06-2-f-mobile-hardening.md`);
- the carried-items file's "Carried to the next change to how the chat screens hold or render chat data".

**Give a verdict on each item:** approved, approved with conditions, changes requested, declined, or refer to Nathan.

1. **What to do with N1 to N9.** The options:
   - **(a) C3 adopts the session's candidate and goes on:**
     - *gains:* closes 36 of the 49;
     - *costs:*
       - five harmless controls fail, a narrow `{ text }` prop among them, which is ordinary code a screen author would write;
       - the remaining 13 and any found by the next round stay open;
       - a fourth round is likely.
   - **(b) Restate the guarantee as a positive list, and record N1 to N9 as known passing classes (recommended):**
     - **the change:** the test comment and the record say what the check refuses, with the planted forms as its specification, rather than what it "follows". They name N1 to N9 beside finding 1's class as forms it does not refuse. A small C3 in the test comment and the record; no change to the checks;
     - **the review:** the delta re-review then holds the reviewer to that list. A form the list says the check refuses, which passes, is a finding; a form in a named class is not;
     - *gains:* a claim that is true and a cycle that ends; the check keeps every refusal C1 and C2 built, and it fails closed;
     - *costs:* the test catches the listed forms, not ordinary refactors such as N1's X2. The manager's reasons: the validator is the primary guard, the data is fixture-only, and the real fix is (c).
   - **(c) Move the screens to view models now, as C3:** DM-38 2.5's design, built by explicit field copy in `rows.ts`, with a check that no contract type reaches `screen.tsx`.
     - *gains:* the strongest guarantee, and a simpler check that N1 to N9 do not reach, since the screen would hold no contract type to narrow;
     - *costs:*
       - a runtime change in the chat screen and its store's consumers, with a full exact-head review;
       - a larger P06.2-F than its brief set out, and its own risk of regressions in a reviewed screen.
   - **(d) Merge C2 as it stands:** the record and the test comment would then claim more than the check does. That is a correction class, so it is not open under rule (a).

   Which, and on what conditions?
2. **The wording,** if (b): you set the guarantee's words in DM-38, so the manager asks you to give the positive list's wording, or the terms it must meet, for the test comment, the record and the brief.
3. **(c)'s timing.** DM-38 2.5 carries (c) to the next change to how the chat screens hold their data. Given N1's X2, should (c) instead become its own work item, named to Nathan before it starts (OD-49) and placed in the order, for example after P06.2-F and before SV4 or P07.2? Recommend a place, or keep 2.5's trigger.
4. **C2's two later code commits** (`082506f`, `816cd60`), which close gaps the session's own probes found in C2's refusals, within Outcomes 1 to 3: are they inside DM-38's terms?
5. **Codex's two threads:** `display-rule.test.ts:339` (a callback by reference) is fixed by C2. `:215` (an object wrapper) is finding 1's class, a named limit. The manager proposes answering and resolving both once your verdict is recorded. Agreed?
6. **Notion:** Implementation Control's status section, the P06.2-F Work Register row and the uses table's row for C2, against `<RECORDS_COMMIT>`.

**The documents the decision touches:** the test comment and the record (C3, if any); the brief (a revision 3); the review log; the carried-items file and the Work Register, if (c) becomes its own item; Notion. No governing Markdown changes in this item.

**What happens next:** the manager applies your verdicts, writes the next prompt with its TypeSafe reading (C3, or the delta re-review), and gives it to Nathan. Item 3's placement goes to Nathan only if you recommend a new item, in OD-32's form.
