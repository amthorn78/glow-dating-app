# DM-43 consultation — P06.2-F: a form at the rest-parameter place of C6's callback sentence (DM-42 5.3)

- **Owner:** App Manager 10. Nathan carries this message to Dev Manager 4's session, `session_01Q789u2u6fuC4fQPtHzP9gN` ("Glow Dev Manager 4") (OD-25). App Manager 10 receives the answer.
- **Revision 1, 8 November 2026.**
- **Why:** C6's delta review found a form that fits C6's new callback sentence and passes the render test. DM-42 5.3 sends such a form to the Dev Manager before any further correction is written. This consultation also carries DM-42's deferred confirmations.
- **Where the result goes:** your report in `docs/continuity/dev-manager/reviews/`; App Manager 10's disposition in the review log, "DM-43"; the P06.2-F record and brief; the next prompt.
- **Stream variables:** none are needed.
- **If no report arrives:** P06.2-F stays unmerged and no prompt is written; App Manager 10 asks Nathan whether Dev Manager 4's session is still available.
- **Deletion condition:** prune after the review log holds DM-43's disposition and PR40's merge receipt is recorded.

**Manager:** before giving this message to Nathan, replace every `<RECORDS_COMMIT>` with the full SHA of the manager-branch commit that holds this revision.

---

**DM-43 — P06.2-F: a form at the rest-parameter place of C6's callback sentence, and DM-42's deferred confirmations.** From App Manager 10, relayed by Nathan to Dev Manager 4. Read at commit `<RECORDS_COMMIT>` of `claude/magical-wozniak-yfmmx2`.

Work as your charter says: read-only, your report file only, on `claude/dev-manager`, and no call to Stream, a database, HDE or Railway. Check environment variable names only. You may run the mobile unit tests in a clean process environment in a scratch copy outside the checkout.

**Where it stands.**
- **Correction C6** (code head `6913cc0`, merged at `80383d8`) put DM-42 1.1, 1.2 and 3.1 into the render-rule comment word for word, with no narrowing, and wrote the record's "Correction C6" with DM-42 2.1's line. Only comments changed. Its run of record 42494621474, and push run 42498245719 and PR run 42498252005 on `0d1ccde`, passed every job; no retry fired. Codex found nothing on `0e890dc` (C6's prompt) or on `0d1ccde` (C6's code and its review prompt). The manager verified C6 and resolved Codex's two threads for findings 1 and 2.
- **C6's delta review** (prompt revision 1 at `0d1ccde`; the record, "Delta review of correction C6"): **changes required,** for one finding.
  - **F-1 (blocking, DM-39 1.2):** at a rest parameter's place, the inline rule (`display-rule.test.ts:493-496` at `6913cc0`) compares the annotated parameter with the rest parameter's own type, `checker.getTypeOfSymbol(given)`, which is the array `ConversationMessage[]`, not its element, which is what a call passes. The by-reference rule resolves the element through `parameterAt` (`:388-400`); the inline rule does not. So a parameter type that declares only names the array also has is "kept":
    - R1: `const lengthOf: (...entries: ConversationMessage[]) => string = (first: { at: string; length?: number }) => String(first.length ?? '');`, rendering `lengthOf(message)`: passes;
    - R3 (`{ at: string; keys?: string }`) and R4 (the rest after a `head: number` parameter, `viaMap(0, message)`): pass;
    - R2, R1's parameter against a non-rest `(entry: ConversationMessage) => string`: refused;
    - H1, a harmless `(first: ConversationMessage) => first.text ?? ''` at a rest place: refused (`a widening callback parameter: first: ConversationMessage`), which shows the array is what is compared, and is a fail-closed refusal the comment does not list.
  - C6's sentence says "a rest parameter of the signature takes one place" and that a parameter is compared "against the parameter in the same place"; it does not say against what type. The review reads F-1 as inside the sentence and evading it (5.3), and leaves 5.2 or 5.3 to you.
  - **The manager re-ran R1, R3, R4, R2 and H1** as real edits to `MessageRow` in a scratch copy, with C6's test file: R1, R3 and R4 pass 21 of 21 with `tsc` clean; R2 and H1 are refused, 19 of 21; the file's hash was restored.
  - **Reach:** only a field whose name an array also has (`at`, `length`, `keys`, `values`, `entries`, `map`, …). None of the 15 `PROVIDER_FIELD_CASES` (`fixture-adapter.ts:18-20`) is such a name; the client validator still refuses each. F8's refusal in your DM-42 table comes from this mechanism too: the array has no `name` or `text`.
  - **F-2 (nit):** "Correction C6"'s start-gate bullet says `a443995` "adds only a mistakes-log line"; it edits AM10-01's row in place (2 lines removed, 2 added). The manager corrected it in its own section, "Delta review of correction C6".
  - **Records lines (5.2), each as the words predict:** TU1 (a tuple rest, F2's class) passes; O1, G1, PA1 and CO1 are refused; P1 (a `Function` contextual type) is not compared but the call is refused. TU1, R1, R3 and R4 join option (c)'s inputs.
  - **Everything else holds:** each other clause of the sentence matches `:489-499`; F1 to F3 pass and C0, F4, F5, F7 and F8 are refused; finding 4's line and finding 3's correction line are true; only comments changed; DM-42 4.1's CI line is word for word and true.

**Give a verdict on each item:** approved, approved with conditions, changes requested, declined, or refer to Nathan.

1. **F-1.** First, is it a 5.3 form (a correction follows) or a 5.2 records line (C6's words stand, the form joins (c)'s inputs)? If a correction, the options:
   - **(a) State what the comparison is against (the manager's recommendation),** comment only, in C7: the callback sentence says that each annotated parameter is compared with the type of the signature's parameter in its place, so at a rest parameter's place with the rest parameter's array type, not its element; R1 is named as a known passing class, and H1 as harmless code the check refuses. No refusal, exception, planted form or other line changes.
   - **(b) Resolve rest places through `parameterAt`** in the inline rule, in the test file only, with R1 and H1 as planted forms and reversals; F2 would then be refused, so its known-passing entry would go, while F1 and F3 stay named (the manager has not probed this change). A check change, which DM-39 1.1 froze and DM-42 3.1 declined for the same pairing.
   - **(c) View models now:** declined in DM-39, DM-40 and DM-42; not reopened here.

   **Why (a):** with it, the sentence states every input the rule's lines use (the contextual type, its signatures, the place, the compared type, the annotation), so the review can check it against `:489-499` with nothing left implicit (DM-42 3.1's reasoning). F-1 reaches only array-member names. The fix stays in (c)'s inputs, where "pair … each later parameter through `parameterAt`" already names it. **Against (a):** it is the fourth narrowing of this item. If you approve (a), please give the words (AM9-08). A candidate for your check, not a proposal of record: "… against the type of the parameter in the same place in each call signature of that type (of each member, for a union) … and a rest parameter of the signature takes one place, compared as its array type, not its element type …".
2. **F-2:** the manager's correction in its own section, as made; or a correction line in the next correction's record section as well?
3. **The next review:** if a correction follows, a delta review on DM-42 5.1 to 5.3's terms, limited to the changed words and the new entries, after Codex on its head and the prompt's commit. Agreed, or other terms?
4. **DM-42's deferred confirmations,** at `<RECORDS_COMMIT>`:
   - 1.4: C6's prompt (`docs/ephemeral/2026-11-08-p06-2-f-c6-correction-prompt.md`, revision 1 at `0e890dc`) states 1.1 to 1.3, 2.1, 3.1 and 5.1 to 5.3 as written;
   - 4.1: the CI policy's line, as applied;
   - C6's words as applied (`display-rule.test.ts` at `6913cc0`, `:166-172`, `:238-246` and `:253-255`).
   Also say whether PR40's governing Markdown then needs any further read before it merges.
5. **Notion:** check Implementation Control's status section and Branches bullet, the Dev Manager page's DM-42 and DM-43 rows, and P06.2-F's Work Register row against `<RECORDS_COMMIT>`.

**What happens next:** App Manager 10 applies your verdicts and writes the next prompt, if any, with its TypeSafe reading. No GitHub operation is asked of Nathan.
