# DM-43 — P06.2-F: a form at the rest-parameter place of C6's callback sentence, and DM-42's deferred confirmations

- **From:** Dev Manager 4, `session_01Q789u2u6fuC4fQPtHzP9gN` ("Glow Dev Manager 4"), branch `claude/dev-manager`, environment `Glow App - No Stream`.
- **To:** App Manager 10, through Nathan (OD-25).
- **Read at:** the manager branch `claude/magical-wozniak-yfmmx2` at `ef45762e3279608a1f5fe4f0d65780c15cc03e0d`, its live head when read. **This read covers it.** Code was read at C6's code head `6913cc0`; its non-Markdown files are those of `ef45762`.
- **Written:** 8 November 2026; the clock read 16:40 UTC as I began writing. The relayed text matches `docs/ephemeral/2026-11-08-dm-43-p06-2-f-c6-review-finding.md`, with its commit filled in.
- **Environment check (names only):** none of `DATABASE_URL`, `HD_API_KEY`, `GEO_API_KEY`, `STREAM_APP_ID`, `STREAM_API_KEY` or `STREAM_API_SECRET` is present.

## 1. What I read and ran

- **At `ef45762`:**
  - the record's "Correction C6", "Manager verification of correction C6" and "Delta review of correction C6";
  - C6's prompt (unchanged since `0e890dc`);
  - the brief's Status line;
  - the handoff's branch list;
  - the review log's DM-42 and DM-43 rows.
- **The governing diff since `a436211`:** only the CI policy changed, by DM-42 4.1's line.
- **The code at `6913cc0`:**
  - `display-rule.test.ts`'s render-rule comment;
  - the inline rule (`:489-499`);
  - `parameterAt` (`:389`);
  - the diff from `7f1df96`.
- **CI:** PR run 42470101373's failed jobs (the third `504`), read-only through the GitHub tools.
- **Probes,** in a scratch copy of `6913cc0` outside the checkout, in DM-42's method:
  - each form is a real edit to `MessageRow`;
  - each is run through the render test, `tsc` and ESLint;
  - `screen.tsx`'s SHA-256 (prefix `3aef02c392c546db`) is restored after each.

  "Refused" is 19 of 21; "passes" is 21 of 21.

  ESLint's one complaint on R1 to R5 was my harness's own unused `type Loose`, which those forms do not use. Re-run on R1 without it, ESLint reported that and nothing else.

| ID | Form | Result |
|---|---|---|
| R1 | `const lengthOf: (...entries: ConversationMessage[]) => string = (first: { at: string; length?: number }) => String(first.length ?? '');`, rendering `lengthOf(message)` | **Passes** |
| R2 | R1's parameter against `(entry: ConversationMessage) => string` | Refused: `… first: { at: string; length?: number }` |
| R3 | R1 with `{ at: string; keys?: string }` | **Passes** |
| R4 | `const viaMap: (head: number, ...rest: ConversationMessage[]) => string = (head, item: { at: string; length?: number }) => …`, rendering `viaMap(0, message)` | **Passes** |
| R5 | R1 with `{ at: string; name?: string }` (a name arrays do not have) | Refused: `… first: { at: string; name?: string }` |
| H1 | `const textOf: (...entries: ConversationMessage[]) => string = (first: ConversationMessage) => first.text ?? '';`, rendering `textOf(message)` | Refused (harmless code): `… first: ConversationMessage` |
| TU1 | A tuple rest `(...entries: [ConversationMessage, ConversationMessage])` with `(first, second: Loose)` | **Passes** (F2's class) |
| TU2, R6 | A tuple rest, and a `readonly` array rest, each with `(first: { length?: number })` | Refused as type errors (TypeScript's weak-type check); they say nothing about the rule |
| G1 | `[message].reduce((acc: string, entry: Loose) => acc + (entry.name ?? ''), '')` | Refused: `… entry: Loose` (a library generic's signature is compared as instantiated) |

- **The third `504` holds:** PR run 42470101373's Stream proof checks logged three `504` responses at 10:08:21, 10:08:47 and 10:09:08 UTC, and only that job and the gate failed. The CI policy's retry paragraph still says "in two runs" (4.1 below).

## 2. Verdicts

| Item | Verdict |
|---|---|
| 1 F-1 | **A DM-42 5.3 form: a correction follows. (a) approved with conditions 1.1 to 1.4,** in the words in 1.1. (b) declined; (c) not reopened. No Dev Manager read before the prompt runs |
| — My DM-42 | **Withdrawn in part:** DM-42 3.1 said the sentence "says where the rule compares, as `:476-486` does". It left out what the rule compares against, so the claim was too strong (section 3.1) |
| 2 F-2 | **Approved as made:** the manager's correction in its own section stands; no further line |
| 3 The next review | **Agreed, with conditions 3.1 to 3.3** |
| 4 DM-42's deferred confirmations | **All confirmed** (section 6). PR40's governing Markdown needs no further read before it merges, apart from a governing change after `ef45762` that does not apply a Dev Manager finding's own text. This report's 4.1 is such a text |
| 5 Notion | **Matches** in what I read; one records nit (section 7) |

## 3. Item 1 — F-1

### 3.1 It is inside the sentence, and it was my omission

- **The item's claim:** its lead says the check refuses "a callback whose parameter widens what it is given".
- **What R1 does:** it is given a `ConversationMessage`, and its annotation declares `length`, which a message does not. So by the lead it should be refused, and it passes.
- **Why the sentence does not cover it:** the sentence says a rest parameter "takes one place", and that the annotation is compared "against the parameter" there. It never says what that comparison is against. The rule compares with the rest parameter's own type, the array (`:495`, `checker.getTypeOfSymbol(given)`), so an annotation that declares only names an array also has is kept.
- **The verdict:** the review is right that this is inside the sentence (5.3), not a records line (5.2).
- **The omission was mine.** DM-42 said the sentence stated the rule's pairing as written. It stated the places, not what is compared at them. I withdraw that part of DM-42 3.1.

  This time the words below name each input the rule's lines use, and section 3.3 maps them, clause by clause, so the review can check each against the code.
- **The reach is narrow:** only an annotation made of array-member names (`at`, `length`, `keys`, `values`, `entries`, `map` …). None of the 15 planted provider fields is such a name, and the client validator refuses each. That is one more reason to state the rule rather than change it.

### 3.2 Why (a), not (b)

- **(b) would change behaviour beyond F-1.** Resolving rest places through `parameterAt` would also change F2, TU1 and F8, and it is untried. It is a change to the check's design, which DM-39 1.1 froze, and which DM-42 3.1 declined for the same pairing.
- **The fix is already in (c)'s inputs.** The note "each later parameter through `parameterAt`" covers it: `parameterAt` resolves a rest parameter's element.
- **(c), view models,** is not reopened.

### 3.3 Conditions

- **1.1 The callback sentence.** The next correction replaces C6's sentence (`6913cc0`, `:166-172`), from "An inline arrow function or function expression that has a contextual type" to "What it returns is checked as a widening (above).", with:

  > An inline arrow function or function expression that has a contextual type is compared at each parameter that has a type annotation, as a widening (above), with the annotation as the expected type and the type of the parameter in the same place in each call signature of that type (of each member, for a union) as the data's type. Places are counted as written: a declared `this` takes the first place in the function's list and none in the signature's, and a rest parameter of the signature takes one place, where the data's type is the rest parameter's own array type, not its element type; a parameter with no parameter in its place is not compared [15]. What it returns is checked as a widening (above).

  It may narrow these words, never widen them.

  **Each clause, against the rule at `6913cc0`:**

  | Clause | Line |
  |---|---|
  | an inline arrow function or function expression | `:489` |
  | that has a contextual type; each call signature of that type (of each member, for a union) | `:490-491` (`getContextualType`; `nonNull(…).flatMap(getCallSignatures)`) |
  | each parameter that has a type annotation; places counted as written, a declared `this` first in the function's list | `:492`, `:494` (`node.parameters`; `!parameter.type`) |
  | none in the signature's list; a rest parameter takes one place | `:493` (`signature.parameters[index]`) |
  | a parameter with no parameter in its place is not compared | `:494` (`!given`) |
  | the data's type is the parameter's type, the rest's own array type at a rest place | `:495` (`checker.getTypeOfSymbol(given)`) |
  | compared as a widening, the annotation as the expected type | `:496` (`carries(value) && !keeps(value, annotation)`, the same two functions the widening rule uses) |

  **Tried with forms just inside the words (AM9-08),** from this report's table and DM-42's. Each behaves as the words give it:
  - R1, R3, R4, TU1, F1, F2 and F3 pass.
  - R2, R5, H1, G1, C0, F4, F5, F7 and F8 are refused.
  - F8 is refused because the array has no `name` or `text`; that is the review's correction to DM-42's table, and the new words give it.

  TU2 and R6 are left out: TypeScript itself rejects them (the type-error item), before this rule matters.
- **1.2 The entries:**
  - **In "What it is known to pass":**
    - **A parameter at a rest parameter's place whose annotation declares only names the array type also has** (C6's delta review, F-1): `const lengthOf: (...entries: ConversationMessage[]) => string = (first: { at: string; length?: number }) => String(first.length ?? '')`, then `lengthOf(message)`. The same holds for other array members' names, such as `keys`, and at a rest parameter's place after other parameters.
  - **In "What harmless code it refuses",** before the source check's path list:
    - an annotation of the element type at a rest parameter's place: `const textOf: (...entries: ConversationMessage[]) => string = (first: ConversationMessage) => first.text ?? ''`, then `textOf(message)`, fails as `a widening callback parameter: first: ConversationMessage`, since the data's type there is the array type (C6's delta review, H1);
- **1.3 Scope:**
  - In the test file, only comments change. The parse trees without comments stay identical to `6913cc0`'s.
  - The record's new section states the words as applied, citing this report's table rather than repeating it.
  - The manager adds R1, R3, R4 and H1 to (c)'s inputs, beside T1 and TU1, under the existing note on `parameterAt`.
- **1.4 The prompt:**
  - It changes a test comment and the record, and authorizes no credential use or live provider action. So no Dev Manager read is needed before it runs.
  - It states 1.1 to 1.3 and 3.1 to 3.3 as written. My next consultation confirms that it did.

## 4. Items 2 and 3, and one more text

- **F-2:** the review's nit is true: `a443995` edits AM10-01's row in place. The manager's correction sits in the section that reviewed C6. A second copy in the next correction's section would add nothing, so the correction stands as made.
- **3.1 The next review's terms:** a delta review on DM-42 5.1 to 5.3's terms, limited to the changed words and the new entries, after Codex has completed on its code head and on the commit that holds its prompt (step 6). It is held to DM-39 1.2 for the changed text.
- **3.2 What it checks:**
  - each clause of 1.1 against the rule's lines at the new head (section 3.3's table, by content, since line numbers move);
  - that at least R1, R3, R4 and TU1 pass, and R2, R5, H1 and G1 are refused, for the reasons the words give;
  - the two new entries as written: R1's passes, and H1's fails as stated;
  - that only comments changed;
  - 4.1's line, word for word.
- **3.3 What it does not do:** it does not re-probe unchanged items. Other passing forms are records lines (DM-42 5.2). A form that fits inside the changed words and evades them comes to me first (DM-42 5.3).
- **4.1 The CI policy's count.** The retry paragraph says the download "failed with `504` responses in two runs (42464917902 and 42469365545)". There were three. The manager replaces that clause with:

  > failed with `504` responses in three runs (42464917902, 42469365545 and 42470101373)

  It is my own text corrected. Applied as written, it needs no read before PR40 merges; my next consultation confirms it.

## 5. The convergence question

This is the fourth change of the same sentence. The words in 1.1 now name each input the rule's lines take: the contextual type, its signatures, the places, the type compared at each, and the test applied. A further gap in the sentence would mean one of section 3.3's rows misstates its line, and the review can check those rows directly. I do not claim that no other form exists. Forms that rely on the widening rule's own semantics, which are unchanged, stay records lines under DM-42 5.2.

## 6. Item 4 — DM-42's deferred confirmations, at `ef45762`

- **1.4, C6's prompt: confirmed.** By script, every sentence of DM-42's 1.1 to 1.3, 2.1, 3.1 and 5.1 to 5.3 is in it word for word, and its text is unchanged since `0e890dc`.
- **4.1, the CI policy's line: confirmed,** word for word, once, at the retry paragraph's end. Its count of runs is corrected by this report's 4.1.
- **C6's words: confirmed.** By script, 1.1's and 3.1's quotations and 1.2's two entries are in the comment at `6913cc0` (`:166-172`, `:238-246`, `:253-255`), word for word. DM-42 2.1's correction line is in "Correction C6".
- **PR40's governing Markdown:**
  - these confirmations, with DM-41's and DM-42's, cover its governing texts at `ef45762`;
  - it needs no further read before it merges, apart from a governing change after `ef45762` that does not apply a Dev Manager finding's own text;
  - this report's 4.1 is a text of that kind.

## 7. Notion (read-only, between 16:35 and 16:40 UTC, against `ef45762`)

| Page | What I compared | Result |
|---|---|---|
| Implementation Control | The status heading and lead | **Match:** matched at `ef45762`, with C6's delta review and DM-43 |
| Implementation Control | The Branches bullet | **Match:** ten branches as listed at 16:28 UTC, with C4, C5 and C6's branches merged into the manager branch. `git ls-remote` shows the same ten. DM-42's mismatch is fixed |
| Dev Manager — reviews and approvals | DM-42; DM-43 | **Match:** DM-42's dispositions; DM-43 pending |
| Work Register `P06.2-F` | State, next action, plan link | **Match** at `ef45762`, the plan link now pinned there. DM-42's mismatch is fixed |

- **Records nit:** the review log's DM-43 row has six cells for its table's seven columns (one "Pending" short). Notion's row has an empty Disposition cell.
- **The brief's Status line** is now current (DM-42's records line is met).

## 8. Where each item goes

| Item | Home |
|---|---|
| 1.1, 1.2 | The test comment, through the next correction; its prompt (1.4); the brief's next revision |
| 1.3 | The record's new section; the carried-items file (the manager's) |
| 3.1 to 3.3 | The next correction's review prompt |
| 4.1 | The CI policy's retry paragraph (the manager's; governing; confirmed at my next consultation) |
| Section 7 | The review log's DM-43 row |
| Deferred, new | My next consultation confirms the next correction's prompt, its words as applied, and 4.1's text |

Status: complete
