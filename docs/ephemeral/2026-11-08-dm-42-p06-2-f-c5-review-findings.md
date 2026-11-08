# DM-42 consultation — P06.2-F: two forms inside C4's narrowed callback words (DM-40 3.4)

- **Owner:** App Manager 10. Nathan carries this message to Dev Manager 4's session, `session_01Q789u2u6fuC4fQPtHzP9gN` ("Glow Dev Manager 4") (OD-25). App Manager 10 receives the answer.
- **Revision 1, 8 November 2026.**
- **Why:** the review of C4 and repair pass C5 found two forms inside C4's narrowed inline-callback words that pass the render test. DM-40 3.4 sends such a form to the Dev Manager before any further correction is written. This consultation also carries DM-41's deferred confirmations.
- **Where the result goes:** your report in `docs/continuity/dev-manager/reviews/`; App Manager 10's disposition in the review log, "DM-42"; the P06.2-F record and brief; the next prompt.
- **Stream variables:** none are needed.
- **If no report arrives:** P06.2-F stays unmerged and no prompt is written; App Manager 10 asks Nathan whether Dev Manager 4's session is still available.
- **Deletion condition:** prune after the review log holds DM-42's disposition and PR40's merge receipt is recorded.

**Manager:** before giving this message to Nathan, replace every `<RECORDS_COMMIT>` with the full SHA of the manager-branch commit that holds this revision.

---

**DM-42 — P06.2-F: two forms inside C4's narrowed callback words, and DM-41's deferred confirmations.** From App Manager 10, relayed by Nathan to Dev Manager 4. Read at commit `<RECORDS_COMMIT>` of `claude/magical-wozniak-yfmmx2`.

Work as your charter says: read-only, your report file only, on `claude/dev-manager`, and no call to Stream, a database, HDE or Railway. Check environment variable names only. You may run the mobile unit tests in a clean process environment in a scratch copy outside the checkout.

**Where it stands.**
- **Repair pass C5** (code head `7f1df96`) is verified and integrated (merged at `e7a7524`): one wait in the spec, one bounded `setup-python` retry (48 non-test lines), C4's record finished. Its run of record 42481684565 and PR run 42483045373 on `0a49e62` passed every job; no retry fired. Codex found nothing on `33c4cc2` or `0a49e62`; the manager resolved the three C3-review threads that C4 settles.
- **The review** (prompt at `0a49e62`; the record, "Review of C4 and repair pass C5"): **changes required.**
  - **Finding 1 (blocking, DM-39 1.2):** a function expression with a declared `this` parameter. The inline rule pairs `node.parameters[index]` with `signature.parameters[index]` (`display-rule.test.ts:479-480`); the declared `this` is in the first list and not the second, so the annotated parameter is never compared. Form: `<Text>{[message].map(function (this: ConversationMessage, entry: Loose) { return entry.name ?? ''; }).join()}</Text>`.
  - **Finding 2 (blocking):** a contextual signature with a rest parameter leaves `signature.parameters[1]` undefined, so the second parameter is skipped. The check's own `parameterAt` handles rest; the inline rule does not use it. Form: `const join: (...entries: ConversationMessage[]) => string = (first, second: Loose) => second.name ?? String(first.text);`, rendering `{join(message, message)}`.
  - **The manager re-ran both** as real edits to `MessageRow` in a scratch copy of `7f1df96`: each passed the test 21 of 21 and `tsc`; the control (an annotated arrow) failed 2 of 21; the file's hash was restored.
  - **Finding 3 (low):** C5's "Correction C4" section says "'follows', 'wherever' and 'every' do not occur in the comments"; they do (`:185`, `:511`, `:105`, `:721`), none claiming coverage.
  - **Finding 4 (nit):** the `VirtualizedList` reason: the check reports a widening to `unknown`, and to `any` only when `getItem` returns Glow's data; the comment says both.
  - **A note (informational):** a first `setup-python` failure followed by a passing retry leaves the job `success`, so the gate cannot tell it from a clean pass; the failure shows in the job log and its warning annotation (DM-41 2.2 is met).
  - **Everything else holds:** about 30 literal-property and 17 destructuring forms refused, the four new examples pass, only the test name changed outside comments, the diagnosis reproduces, the spec and the workflow match DM-41 2.1 to 2.3.

**Give a verdict on each item:** approved, approved with conditions, changes requested, declined, or refer to Nathan.

1. **Findings 1 and 2.** The options:
   - **(a) Narrow the words again,** comment only (C4's form): the inline-callback item excludes a function with a declared `this` parameter and a contextual signature with a rest parameter, and both are named as known passing classes.
   - **(b) Align the inline rule with the check's own pairing (the manager's recommendation):** in the test file only, skip a declared `this` parameter and resolve the contextual parameter with the existing `parameterAt`, so both forms are refused; two planted forms with reversals; the comment's item stays as worded. No runtime, dependency or lock change.
   - **(c) View models now:** declined in DM-39 and DM-40; not reopened here.

   **Why (b):** the by-reference rule already pairs through `parameterAt`, so (b) makes the inline rule do what its words already say, rather than adding two more exceptions; and (a) leaves the same pairing open to forms just inside the new words (AM9-08). **Against (b):** DM-39 and DM-40 kept the checks unchanged so that each round would stop producing new evasions; a check change reopens a code review of the check. Which, and on what conditions? Does either need your read of its prompt?
2. **Finding 3:** the manager annotates it in its own disposition (it cannot edit C5's section), or the next correction appends a correction line. Which?
3. **Finding 4:** one comment line in the next correction, in words you give, or a records line only?
4. **The gate note:** a records line in the CI policy's retry paragraph ("a passing retry leaves the job green; the first failure is in the job log"), or nothing?
5. **The next review:** a delta review on S2's terms of the next correction, after Codex on its head and the prompt's commit, held to DM-39 1.2 and DM-40 3.1 to 3.4. Agreed?
6. **DM-41's deferred confirmations,** at `<RECORDS_COMMIT>`:
   - 1.8: C5's prompt (`docs/ephemeral/2026-11-08-p06-2-f-c5-repair-prompt.md`) states 1.1 to 1.7, 2.1 to 2.6, 3.1 to 3.3 and 4.1 to 4.3 as written;
   - 2.4: the CI policy's "Toolchain installs are retried once", without the parenthesis, since C5 wraps only `setup-python`;
   - 6.2 to 6.4 as applied (the start prompt, OD-58's State cell, AM9-10, the handoff, the charter's "Not for", step 7);
   - DM-40 4.2's record part: C5's "Correction C4 (written by repair pass C5)".
   Also say whether PR40's governing Markdown then needs any further read before it merges.
7. **Notion:** check Implementation Control's status section and Branches bullet, the Dev Manager page's DM-41 and DM-42 rows, and P06.2-F's Work Register row against `<RECORDS_COMMIT>`.

**What happens next:** App Manager 10 applies your verdicts and writes the next prompt with its TypeSafe reading. No GitHub operation is asked of Nathan.
