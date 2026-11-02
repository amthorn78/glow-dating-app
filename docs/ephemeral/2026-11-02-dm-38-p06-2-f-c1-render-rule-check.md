# DM-38 consultation — P06.2-F: the render-rule check's design after C1's delta re-review

- **Owner:** App Manager 9. Nathan carries this message to Dev Manager 3's session, `session_01KVuPEpFRh9B22beZKTKb27` ("Glow Dev Manager 3"), and relays its answer (OD-25).
- **Revision 1, 2 November 2026.**
- **Why:** C1's delta re-review asks for changes: the render-rule test's type check does not hold its claim "through any binding". Step 6's rule (a) puts the findings before the merge, but the fix's design is open (extend the check, narrow its claim with cheap hardening, or change how the screens hold data), and the check guards the display rule (ADR 0003; PF01 §7), a member-privacy boundary. Step 6 and the charter send such a fix to the Dev Manager first.
- **Where the result goes:** your report in `docs/continuity/dev-manager/reviews/`; the manager's disposition in the [review log](../continuity/dev-manager/README.md), "DM-38"; the dispositions in the P06.2-F record, "Delta re-review of correction C1"; the correction's design in the brief, revision 2.
- **Stream variables:** none are needed.
- **If no report arrives:** P06.2-F stays unmerged and no correction prompt is written; the manager asks Nathan whether the session is still available.
- **Deletion condition:** prune after the review log holds DM-38's disposition and PR40's merge receipt is recorded.

**Manager:** before giving this message to Nathan, replace every `<RECORDS_COMMIT>` with the full SHA of the manager-branch commit that holds this revision.

---

**DM-38 — P06.2-F: the render-rule check's design after C1's delta re-review.** From App Manager 9, relayed by Nathan. This consultation is revision 1, at commit `<RECORDS_COMMIT>` of `claude/magical-wozniak-yfmmx2`.

Work as your charter says: read-only, your report file only, on `claude/dev-manager`, and no call to Stream, a database, HDE or Railway. Check environment variable names only. You may run the mobile unit tests in a clean process environment in a scratch copy outside the checkout.

**Where it stands.**
- **P06.2-F** (PR40, full scope) closed seven fixture-only mobile items. Its exact-head review found that item 2's render-rule test (`apps/mobile/src/chat/display-rule.test.ts`), which checks from source that `screen.tsx` and `rows.ts` render only contract fields, read only paths through six variable names, so a renamed binding passed it.
- **Correction C1** (code head `0881db5`; one test file, +310 −12; no runtime line) kept that source check and added a type check on the installed TypeScript compiler that finds Glow's data by its type, with 22 planted forms, each failing for a named reason. Its run of record passed all eight jobs. The manager verified it (the record, "Manager verification of correction C1").
- **C1's delta re-review: changes required.** C1 closes every planted form and weakens no earlier check, but the type check tracks Glow's data only by the value's own top-level type (or arrays of it, four deep). More than 20 edits confined to the two files render a provider-shaped field and pass the test, `tsc` and ESLint: data held in a wrapper, closure, container, Promise, generator or class field; a declared function passed by reference; a local type guard; aliased `Reflect` or `Object.assign`; and two exceptions wider than they say. Findings 1 to 5 fall in the review prompt's correction classes; 6 to 8 are nits. The manager re-ran three as real edits; each passed (the record, "Delta re-review of correction C1", which has the table).
- **What else guards the display rule at fixture scope:** the client boundary validates every response with the generated validators and refuses a provider-shaped field (the display-rule test's 15 provider-field cases), and the screens are typed against the generated contracts. The render-rule test is the second layer, which item 2 asked for so that the rule "does not rest on the client validator alone".

**Read, at `<RECORDS_COMMIT>`:**
- the P06.2-F brief, item 2 and "Correction C1" (`docs/planning/p06-2-f-mobile-hardening.md`);
- the P06.2-F record's "Correction C1", "Manager verification of correction C1" and "Delta re-review of correction C1" (`docs/testing/evidence/2026-11-01-p06-2-f-mobile-hardening.md`);
- `apps/mobile/src/chat/display-rule.test.ts`, and as needed `screen.tsx`, `rows.ts` and ADR 0003;
- the manager workflow, step 6 ("Fix or carry, by rule"); the review log's "Deferred conditions".

**Give a verdict on each item:** approved, approved with conditions, changes requested, declined, or refer to Nathan.

1. **The disposition.** The manager reads findings 1 to 5 as rule (a): fixed before the merge, in a correction pass C2 of the same file and the record, then another delta re-review (C2 would change no non-test line). Nits 6 and 8 ride along; nit 7 stays a recorded limit. Agreed?
2. **The fix's design.** The options:
   - **(a) Extend the check structurally:** follow Glow's data through object properties, closures, containers, Promises, generators and class fields, functions passed by reference, user-defined type guards and library generics, with no depth limit that fails open; narrow both exceptions; plant every new form. *Gains:* closes the forms found. *Costs:* a much larger test (several hundred lines), still not complete, since no source check proves a data-flow property of arbitrary TypeScript; a likely next review finds more forms; more risk of failing harmless screen code.
   - **(b) Narrow the claim and close whole classes cheaply (recommended):**
     - **say what it guarantees:** the test comment, the record and the brief's Outcome 1 state the real guarantee. The check follows Glow's data by its own type at a property read, a destructuring, a spread, an enumeration, an `in` check, and wherever the value is passed, returned, assigned, annotated, or given as a prop or an inline callback parameter. It does not follow data held inside another value, a function passed by reference, another module or a template literal, and those are named as limits;
     - **refuse, by identifier and not by text,** any user-defined type predicate or assertion signature in the two files, and any reference to `Reflect`, or to an `Object` member other than `freeze`, however aliased;
     - **narrow the two exceptions to their words:** the dependency list only as an argument of a React hook call; the destructuring initializer only when no enclosing pattern is annotated;
     - **fail if a `GLOW_DATA` path is missing,** or no checked type comes from it (nit 6);
     - **correct the Mobile row** (nit 8);
     - **plant one form per closed class** (finding 3's guard and aliases; finding 4's two exceptions).

     *Gains:* every claim true; four of the review's classes closed by refusals that cannot be renamed around; a small change. *Costs:* findings 1 and 2's classes (data held in another value; a function by reference) stay open as named limits, so the test catches an accidental read of a field, not a deliberate evasion. The manager's reasons: an author who means to evade can also edit the test, and the validator is the primary guard.
   - **(c) Change how the screens hold data:** the screens render only view models built by explicit field copy (as `rows.ts` does for the list), so the check reduces to "no contract type reaches `screen.tsx`". *Gains:* the strongest guarantee, and a simpler check. *Costs:* a runtime change in the chat screen and its store's consumers, outside C1's scope, with a full exact-head review; it fits P06.3's UI work better. The manager would record it as a candidate for P06.3's brief under (b).
   - **(d) Carry it all to P06.3 with the record corrected:** rule (a) does not allow it for findings in a correction class.

   Is (b) adequate for a second-layer check of the display rule, and on what conditions? If not, which?
3. **The brief.** Under (b), Outcome 1's "fails when `screen.tsx` or `rows.ts` renders a provider-shaped field through any binding" claims more than a source check can show; brief revision 2 restates it as the guarantee above, with the limits named. Agreed, and is that a change the brief's Dev Manager terms require you to read before C2's prompt runs, or does it apply your words without a further read (DM-03 G2)?
4. **The manager's own share.** The manager's verification of C1 re-ran the planted forms and the named evasion, then repeated the session's "through any binding" in the review prompt, Notion and its reply on Codex's thread without trying forms of its own (AM9-03). Is the prevention in that entry (a completeness claim is verified with forms the session did not list, or quoted as the session's) enough?
5. **Your deferred reads,** which wait on your next consultation (the review log's "Deferred conditions"):
   - **DM-37 2.7:** PF01 §7's release gate, as PF01 1.17 applies it in your words;
   - **DM-37 4.1 to 4.4:** the first A05 message as sent (`docs/ephemeral/2026-11-01-a05-first-decision-message.md`), with Nathan's answers in OD-55.
6. **Notion:** Implementation Control's status section, the P06.2-F Work Register row and the uses table's row for C1's delta re-review, against `<RECORDS_COMMIT>`. The status section's standing bullets were brought up to date at this batch's sync (AM8-22).

**The documents the decision touches:** the test and the record (C2), the brief (revision 2), the review log, Notion, and P06.3's brief if (c) is recorded for it. No governing Markdown changes in this item.

**What happens next:** the manager applies your verdicts, writes C2's prompt with its TypeSafe reading, and gives it to Nathan. Nothing goes to Nathan to decide unless you refer an item to him.
