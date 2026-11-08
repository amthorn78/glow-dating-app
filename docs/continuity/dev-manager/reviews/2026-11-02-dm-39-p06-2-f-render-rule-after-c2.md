# DM-39 — P06.2-F: the render-rule check after C2's own probes

- **Consultation:** DM-39, revision 1, from App Manager 9, relayed by Nathan (OD-25).
- **Reviewer:** Dev Manager 3, `session_01KVuPEpFRh9B22beZKTKb27`, branch `claude/dev-manager`.
- **Date:** 2 November 2026.
- **Commit read:** `6a9a6b5f60e8bfda4139e461c5bd182911db2408`, the head of `claude/magical-wozniak-yfmmx2`. **This read covers `6a9a6b5`** (DM-03 G2). `main` is `bac3c19`.
- **Environment (names only):** none of `DATABASE_URL`, `HD_API_KEY` or `GEO_API_KEY` is set, and no `STREAM_*` name is present.
- **What I did not do:** I called no provider, database, HDE, Railway or the TypeSafe API. I wrote nothing in the checkout except this report.
- **What I ran, all in a clean process environment:**
  - **The scratch copy:** `apps/mobile` and `packages` at `6a9a6b5`, extracted by `git archive` outside the checkout, then `npm ci --ignore-scripts`. The hashes match the record: `screen.tsx` `3aef02c3…`, `rows.ts` `bdce90ca…`, the test `262e20e3…`.
  - **The test:** `display-rule.test.ts` passed 21 of 21.
  - **Probes:** seven, each an edit to the scratch `screen.tsx`, then the render test, `tsc --noEmit` and ESLint, then the file restored and its SHA-256 checked (section 3).

## 1. What I read

- **The record** (`docs/testing/evidence/2026-11-01-p06-2-f-mobile-hardening.md`): "Correction C2", all of it, and "Manager verification of correction C2".
- **The test** at `816cd60` (byte-identical at `6a9a6b5`): its render-rule comment, and the diffs of `082506f` and `816cd60`.
- **The brief:** "Correction C2", the revised Outcome 1 of "Correction C1", and "Sessions".
- **The carried-items file:** "Carried to the next change to how the chat screens hold or render chat data".
- **My DM-38 report,** sections 4 and 5.
- **The records:**
  - the review log's DM-38 disposition and DM-39 row, and "Deferred conditions";
  - AM9-03's prevention;
  - the handoff's next steps.
- **PR40's register and start-prompt paths** against `main`.
- **Notion, read-only:** *Implementation Control*'s status section (as section 9 says); the Work Register row P06.2-F; the uses table's row for C2.

## 2. Verdicts

| Item | Verdict |
|---|---|
| 1 N1 to N9 | **Approved with conditions 1.1 to 1.4: option (b), with no change to the checks.** My DM-38 section 4 wording is withdrawn (1.4) |
| 2 The wording | **Section 4:** a core paragraph word for word, and the terms the lists must meet |
| 3 (c)'s timing | **Keep 2.5's trigger, with a backstop (3.1) and one condition (3.2).** No new item, so nothing goes to Nathan |
| 4 C2's two later commits | **Approved: inside DM-38's terms** |
| 5 Codex's threads | **Agreed,** with a third thread (`:133`) answered too |
| 6 Notion | **Matches `6a9a6b5` in what I read, with one mismatch:** a recommendation on (c)'s timing that the repository does not make |

## 3. What I tried

| # | Edit to `screen.tsx` | Render test | `tsc` / ESLint |
|---|---|---|---|
| X2 | **N1's ordinary refactor:** `<Narrow entry={message} />`, where `Narrow`'s prop is `{ text: string \| null }` and it passes `entry` to `Wide`, whose loose prop renders `entry.name` | **Passes**, as reported | pass / pass |
| X2P | **The same, with `Narrow`'s prop written as `Pick<ConversationMessage, 'text'>`** | **Fails:** `a widening to { name?: string \| undefined; text: string \| null; }: entry` | pass / pass |
| HL | **A harmless narrow prop,** `{ text: string \| null }`, rendering only `entry.text` | Passes (the session's candidate refuses it) | pass / pass |
| HP | **The same harmless prop, written as `Pick<ConversationMessage, 'text'>`** | Passes | pass / pass |
| HVL | **The variable form of N1:** `const plain: { text: string \| null } = message`, then a loose variable from `plain`, rendering `loose.name` | **Passes** | pass / pass |
| HVW | **The same, with `plain` typed `Pick<ConversationMessage, 'text'>`** | **Fails:** `a widening to { text: string \| null; name?: string \| undefined; }: plain` | pass / pass |
| HV | **A harmless `Pick<ConversationMessage, 'text'>` variable,** rendering only `plain.text` | Passes | pass / pass |

**What it shows:** a narrow type built from the contract's own keeps Glow's identity, for a prop and for a variable alike. The harmless use passes, and the evasion is caught, as the record says of `Pick<>` and `Omit<>`. N1 needs a narrow type declared outside `GLOW_DATA`.

## 4. Items 1 and 2 — what to do with N1 to N9, and the wording

### 4.1 The decision: option (b)

**Why (b):**
- the claim becomes true and testable;
- the cycle ends, because a passing form outside the list becomes a recorded limit, not a defect;
- option (c) replaces this check (DM-38 2.5), so more refusals here are spent work;
- nothing reaches real people before P11: the data is fixture-only, and the client validator is the first guard.

**Why not the others:**
- **(a):** its harmless cost is smaller than the consultation states.
  - Two of the five controls, the narrow prop and the narrow variable, have a spelling that passes and keeps the protection (section 3).
  - One is a flaw in matching comment text.

  But (a) leaves 13 forms open, and each new refusal invites forms near it: a fourth round.
- **(c) as C3:** a runtime change outside P06.2-F's brief. If it is ever brought forward, it is its own item.
- **(d):** rule (a) does not allow it.

**Conditions:**
- **1.1 C3 changes only the test comment, the record and the brief.** No refusal, exception or planted form changes, and the delta re-review confirms that the code is otherwise unchanged from `816cd60`.
- **1.2 The delta re-review's standard:**
  - a form that evades a listed refusal is a finding;
  - a form outside the list that passes is recorded as a known passing class (a records line), not a finding;
  - the reviewer tries forms of its own against each listed refusal.
- **1.3 What C2 learned goes to option (c)'s brief:**
  - the record keeps the 49 forms, the candidate's three rules with their measured results, and section 3's `Pick<>` result;
  - (c)'s brief takes N1 to N9's forms as forms its check must refuse;
  - it takes today's harmless controls (the candidate's five, and F0's family) as forms its check must pass.
- **1.4 My DM-38 section 4 wording is withdrawn.**
  - "Follows Glow's data by its own type … wherever the data is passed …" claimed protection over code paths the check does not track, as N1 to N9 show.
  - It was an "every" over arbitrary code, the error DM-38 4.2 warns briefs against, and I made it myself.
  - Section 4.2's wording replaces it.

### 4.2 The wording

**The core paragraph, word for word.** It replaces DM-38 section 4's paragraph in the test comment, the record and the brief:

> **What the check does (DM-39).** It refuses the forms listed below, and its planted forms are that list's specification: a form that evades a listed refusal is a defect, and any other form that passes is a limit, recorded when found. It treats a value as Glow's data while the value's type declares a field in a `GLOW_DATA` file, and it does not check the value once its type declares none, for example after a narrower type declared outside those files; a narrower type built from the contract's own, such as `Pick<>` or `Omit<>`, keeps it Glow's data. The forms it is known to pass are named below; probes found them, and more may exist. It refuses some harmless code, which fails closed. It is a test over two files' source, not a proof. The client validator is the first guard, and view models built by explicit field copy (DM-38 2.5) are the structural fix.

**The terms the rest must meet:**
- **What it refuses:** the comment's present "What it refuses, in its own terms" list stays. Each item names, by ID, the planted forms that pin it.
- **What it is known to pass:**
  - finding 1's class (data held inside another value);
  - N1 to N9, each with one example from the record's table, N1 naming X2 as an ordinary refactor;
  - another module;
  - a template literal's coercion.

  The list says where these came from: C1's exact-head review, its delta re-review, and C2's 256 probe forms.
- **What harmless code it refuses:** the record's false-positive list, each item failing closed:
  - F0's family;
  - inferred predicates, such as `.filter(text => text !== null)`;
  - Node's `assert`;
  - the source check's path list.

  The next author changes the design (2.5), not the check.
- **No words that claim coverage of code paths:** no "follows", "any", "every", "all" or "wherever" applied to code (DM-38 4.2).
- **Where it goes:**
  - the test comment;
  - a new "Correction C3" section of the record, which supersedes C1's and C2's guarantee wording without editing it;
  - the brief's revision 3, where C1's Outcome 1 and C2's Outcome 6 point to it.
- **Its read:** applied in these terms, it needs no read before C3's prompt runs. The brief is not governing Markdown. My next consultation confirms it.

## 5. Item 3 — option (c)'s timing

**Keep DM-38 2.5's trigger. X2 is inside it:** an intermediate component that takes messages is "a helper or control that takes messages". So the change that would bring X2 in brings (c) with it.
- **3.1 The backstop:** (c) lands before P11 serves the chat reads, at the latest.
  - It goes in the P11 plan's list of what must hold before the reads are served, with a pointer from the carried-items section.
  - If the trigger is missed, the backstop still catches it before real data reaches the screens.
- **3.2 Every brief that touches `src/chat/screen.tsx` or `rows.ts` checks 2.5's trigger** and says whether it applies. P06.3's brief is included.
- **Why not its own item now:**
  - the data is fixture-only;
  - the trigger covers the ordinary-refactor class;
  - the backstop covers a missed trigger;
  - an earlier item would delay P06.3 and SV1 to SV4 for a runtime refactor of a reviewed screen, with nothing at stake yet.

## 6. Item 4 — C2's two later code commits

**Approved: they are inside DM-38's terms.**
- **`082506f`** compares a by-reference function's return, as an inline callback's return is already checked. That is 2.1's "as an inline callback is". Pinned by C2-1e.
- **`816cd60`** extends:
  - 2.2's refusal by signature to a guard given by reference (C2-2e);
  - 2.6's refusal by identifier to a destructuring by key (C2-3c, C2-3d).
- **Neither adds an exception:** both add only refusals and planted forms (2.1's stop rule), and today's two files pass.
- **Two new false positives came with C2's predicate refusal:** an inferred predicate, as in `.filter(text => text !== null)`, and Node's `assert`. They fail closed, and they go in the false-positive list (section 4.2).

## 7. Item 5 — Codex's threads

**Agreed,** once the review log records DM-39. Each reply states only what the record shows:
- **`:339`:** fixed in C2 (DM-38 2.1; planted C2-1a to C2-1e).
- **`:215`:** finding 1's class, a named limit. Option (c) comes at the next change to how the chat screens hold their data, and before P11 serves the chat reads at the latest (3.1).
- **Also `:133`,** which the handoff lists: its earlier reply repeated "through any binding" (AM9-03). The correcting reply states section 4.2's wording.

## 8. Records

- **DM-38's application is confirmed:**
  - brief revision 2 quotes DM-38 section 4. That wording is now withdrawn (1.4), and revision 3 replaces it;
  - AM9-03's prevention takes 4.1 and 4.2 in the report's words;
  - 2.5's Deferred row is open.
- **PR40's register and start-prompt changes against `main`:**
  - OD-55 and OD-56, read in DM-38;
  - the next-manager start prompt's history line, now naming App Manager 9 (OD-56).

  No other governing path changes.
- **The Deferred conditions:**
  - 2.5's row gains the backstop (3.1);
  - a new row for 1.3: the inputs carried to (c)'s brief.

## 9. Notion

- ***Implementation Control*:**
  - **What I read:** the lead's first entry (matched to `6a9a6b5`), Phase in full, and the first 1,500 characters of each other standing bullet (Next items, Dev Manager, Manager, Main, Branches, Mistakes log). These match `6a9a6b5`.
  - **What I did not read:** the rest of each long bullet, and the section's history.
  - **The branch list** (six) matches `git ls-remote`.
- **One mismatch:** the lead and P06.2-F's Work Register row both say the manager recommended "view models as their own item".
  - The consultation and the review log's DM-39 row make no recommendation on (c)'s timing; they ask it.
  - The repository wins (OD-27). The Notion text says the timing was asked, and now follows DM-39 section 5.
- **The uses table's row "P06.2-F correction C2 (render-rule check)"** matches the brief: a correction, v8.2, the TypeSafe cell the brief records, *Nathan's pick* "not recorded", and PR40.

## 10. Where each item goes

- **C3's prompt:** 1.1, and section 4.2's wording and terms.
- **The record, "Correction C3":** 1.3 and section 4.2.
- **The brief, revision 3:** section 4.2.
- **The delta re-review's prompt:** 1.2.
- **The P11 plan, and the carried-items file:** 3.1, with 3.2 and 1.3 in the carried-items section.
- **Codex's threads:** section 7.
- **The review log:**
  - DM-39's disposition;
  - the Deferred updates in section 8.
- **Notion:** section 9's mismatch.

Status: complete
