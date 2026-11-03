# DM-40 consultation — P06.2-F: C3's delta re-review, and OD-57's governing texts

- **Owner:** App Manager 9. Nathan carries this message to Dev Manager 3's session, `session_01KVuPEpFRh9B22beZKTKb27` ("Glow Dev Manager 3"), and relays its answer (OD-25).
- **Revision 1, 3 November 2026.**
- **Why:** C3's delta re-review asks for changes. Three of its own forms evade refusals that the test comment lists, and two of the comment's statements are false. Step 6's rule (a) puts them before the merge. The fix can be made in the comment and the records, inside DM-39 1.1, or in the check, which departs from 1.1. That design choice for the display rule comes to you first, as DM-38 and DM-39 did. PR40 now also carries governing Markdown for Nathan's OD-57, which you read before it merges; DM-39 4.2 also left its wording for your next consultation to confirm.
- **Where the result goes:**
  - your report in `docs/continuity/dev-manager/reviews/`;
  - the manager's disposition in the [review log](../continuity/dev-manager/README.md), "DM-40";
  - the P06.2-F record's "Delta re-review of correction C3";
  - the brief's revision 4 and the next correction's prompt.
- **Stream variables:** none are needed.
- **If no report arrives:** P06.2-F stays unmerged and no prompt is written; the manager asks Nathan whether the session is still available.
- **Deletion condition:** prune after the review log holds DM-40's disposition and PR40's merge receipt is recorded.

**Manager:** before giving this message to Nathan, replace every `<RECORDS_COMMIT>` with the full SHA of the manager-branch commit that holds this revision.

---

**DM-40 — P06.2-F: C3's delta re-review, and OD-57's governing texts.** From App Manager 9, relayed by Nathan. This consultation is revision 1, at commit `<RECORDS_COMMIT>` of `claude/magical-wozniak-yfmmx2`.

Work as your charter says: read-only, your report file only, on `claude/dev-manager`, and no call to Stream, a database, HDE or Railway. Check environment variable names only. You may run the mobile unit tests in a clean process environment in a scratch copy outside the checkout.

**Where it stands.**
- **Correction C3** (branch `ccr-7506019b-5rfdfn`, code head `f87e8b1`; merged at `cfab39b`) applied DM-39 section 4.2:
  - the test comment holds your core paragraph word for word, then the three lists;
  - each refusal names the planted forms that pin it, or says that none does;
  - only comments changed;
  - its run of record, 41553218994, passed all eight jobs.
- **Its delta re-review** (prompt revision 2 at `b2904a4`; the record, "Delta re-review of correction C3"): **changes required.**
  - **What holds:** only comments changed, the core paragraph is word for word, every bracket is true, and each known-passing example passes.
  - **What does not:** about 90 of its own forms were tried, and three of them evade listed refusals:
    - **Finding 1:** a callback "passed by reference (… an object's method)". An object literal's method shorthand, `{ line(entry: Loose) { return entry.name ?? ''; } }`, gets neither the inline nor the by-reference comparison. It also passes as a JSX prop, through an overloaded interface, as a class instance under that interface type, and in `rows.ts`. The arrow property, `{ line: shout }` and `{ line }` are refused.
    - **Finding 2:** the destructuring exception's "whose reads the pattern's own check covers". When the parameter's type comes from context, not an annotation, the pattern is typed `Loose` and the Glow-data default is exempt. An example is `const caption: (entry?: Loose) => string = ({ name } = message) => name ?? ''`. It is the same shape as C1's delta re-review finding 4.
    - **Finding 3:** the listed "destructuring assignment" is refused only as an `=` expression. A `for…of` head, `for ({ ...rest } of conversation.messages) break;`, passes.
  - **Finding 4 (should fix, low):** the source check's text match misses more forms than the four the comment names. Examples are `(message)as{…}`, `'/*'` in a string, `'name'in message` and `Reflect['get']`. The type check refuses each one tried.
  - **Finding 5 (should fix, low):** `VirtualizedList` is given F0's `ArrayLike` and `Iterable` reasons, but its `data` prop is `any`.
  - **Nits 6 to 9:** C2's probe IDs are not unique; the 49th form is N4 or N5; the comment and the record attribute the source-check misses differently; and "whatever its key" is a coverage phrase, since a union-typed key is not refused.
  - **Severity:** none is blocking, given fixture scope and the validator as the first guard.
  - **Codex found findings 1 to 3 again** on `7983b31`, as three P2 threads (`display-rule.test.ts:452`, `:411`, `:448`), with the same forms.
- **The manager's re-run** (a scratch copy of `f87e8b1`, each a real edit to `screen.tsx` with its SHA-256 checked after restore):
  - findings 1, 2 and 3 each passed the test (21 of 21) and `tsc`;
  - the arrow-property control was refused;
  - `VirtualizedList.d.ts:203` types `data` as `any`.
- **Focus 9, the unpinned refusals:** the review's view is to keep them as marked, plant nothing before the merge, and carry them, with its forms, to option (c)'s brief. It is not a correction class.
- **OD-57** (Nathan, 3 November 2026: *"Make clear note that playwright and similar support can be implemented via CLI environments"*):
  - it is recorded in the owner-direction register, and noted in the manager workflow's step 3 and `apps/mobile/AGENTS.md`, both governing Markdown, and in the local setup, the environment inventory and the mobile README;
  - `playwright install` stays forbidden in a cloud container;
  - a CLI environment may install the pinned Chromium and run the rendered suite when a prompt authorizes it, and CI's run stays the run of record.

**Read, at `<RECORDS_COMMIT>`:**
- the record's "Correction C3", "Manager verification of correction C3" and "Delta re-review of correction C3" (`docs/testing/evidence/2026-11-01-p06-2-f-mobile-hardening.md`);
- `apps/mobile/src/chat/display-rule.test.ts`, its comment above all;
- your DM-39 report, sections 4 and 5;
- the brief's "Correction C3" (`docs/planning/p06-2-f-mobile-hardening.md`), revision 3, which applies your section 4.2;
- for item 6, the governing texts: OD-57's row in `docs/continuity/owner-directions.md`, the manager workflow's step 3 (its last bullet on environments) and `apps/mobile/AGENTS.md` (the `test:rendered` bullet), with `git diff b2904a4~2 b2904a4` as the guide.

**Give a verdict on each item:** approved, approved with conditions, changes requested, declined, or refer to Nathan.

1. **Findings 1 to 5.** The options:
   - **(a) C4 changes the comment and the records only (recommended):**
     - **the change:** the three listed items are narrowed to the syntax the check refuses, and the three forms are named as known passing classes;
     - **the narrowed items:** an inline arrow or function expression; a declared function, a `useCallback` result or an object property holding a function, given by reference; the destructuring exception's claim that the pattern's own check covers its reads, limited to a pattern typed as Glow's data, with a contextually typed parameter named as a known passing class (the exception's code unchanged); a destructuring assignment only as an `=` expression;
     - **the other corrections:** the source-check paragraph says that its text match is evaded by spacing, comments, strings and bracket forms, which the type check refuses, with the review's examples; and the `VirtualizedList` reason is corrected;
     - **gains:** inside DM-39 1.1; the list becomes true; a small change;
     - **costs:** the list claims less than it did; a later round may find evasions inside the narrowed words, though naming syntax rather than categories makes that less likely.
   - **(b) C4 changes the check for findings 1 to 3:**
     - **the change:** method declarations are compared like by-reference functions; a contextually typed destructuring parameter's default is checked; a `for…of` destructuring head is refused; each gets planted forms;
     - **costs:** it departs from DM-39 1.1, and each new refusal invites forms near it (your 4.1), in a check that option (c) replaces.
   - **(c) View models now:** your DM-39 4.1 declined this for P06.2-F. If it is brought forward, it is its own item.

   Which, and on what conditions?
2. **The wording,** if (a): give the narrowed items' words, or the terms they must meet, as in DM-39 section 4.2.
3. **C4's review.** OD-53 S2 gives a correction that answers review findings a delta re-review. Four rounds have each found forms beyond the stated claim. The manager proposes a delta re-review held to DM-39 1.2 for the changed items only: the narrowed words, the newly named classes, the corrected reasons, and a check that only comments changed. It would not re-probe the unchanged items, which this review tried. Agreed, or what standard?
4. **Focus 9:** the manager proposes accepting the review's view. The unpinned refusals stay marked, and they go with the review's forms (findings 1 to 4 and O5) into DM-39 1.3's inputs for option (c)'s brief. Agreed?
5. **Nits 6 to 9 and the records lines:**
   - nits 6 and 7 go into C4's record section and (c)'s inputs (forms by class and ID, with the duplicates named);
   - nits 8 and 9 go into C4's comment edit;
   - the test name at `:670`, "whatever the validators let through", is a non-comment line, so it is carried to (c)'s brief rather than changed under 1.1.

   Agreed?
6. **OD-57's governing texts,** your pre-merge read under the charter:
   - **the texts:** the manager workflow's step 3 sentences and `apps/mobile/AGENTS.md`'s `test:rendered` bullet, at `<RECORDS_COMMIT>`. Do they apply OD-57 as Nathan gave it, without loosening another rule?
   - **DM-39 4.2:** your report said that your next consultation confirms the brief's revision 3 applies your section 4.2 wording. Does it?
7. **Notion:** check these against `<RECORDS_COMMIT>`:
   - Implementation Control: its status section, the "One item at a time" line of its operating procedure, and its "Standing directions" line;
   - the P06.2-F Work Register row;
   - the register copy's OD-57 row;
   - the uses table's two rows for C3's delta re-review.

**The documents the decision touches:**
- the test comment and the record (C4, if any), and the brief (a revision 4);
- the review log and the carried-items file (DM-39 1.3's inputs);
- Notion.

No governing Markdown changes in this item beyond OD-57's.

**What happens next:** the manager applies your verdicts. It writes the next prompt with its TypeSafe reading (C4, or another, as you decide) and gives it to Nathan. The merge waits on C4's review and on this read.
