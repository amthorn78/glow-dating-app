# P06.2-F correction C7 prompt — the compared type at each place (DM-43)

- **Owner:** App Manager 10. Nathan starts this session manually, in the `Glow App - No Stream` environment (OD-36), and relays its report.
- **Revision 1, 8 November 2026.**
- **Durable brief:** [P06.2-F — Mobile hardening and P06.2's carried follow-ups](../planning/p06-2-f-mobile-hardening.md), revision 7, its section "Correction C7". The design is [DM-43](../continuity/dev-manager/reviews/2026-11-08-dm-43-p06-2-f-c6-review-finding.md), sections 1, 3 and 4.
- **Where the result goes:** the session's change to the render-rule comment in `apps/mobile/src/chat/display-rule.test.ts`, and the record's new "Correction C7" section, on its own branch; the run of record, the Foundation push run on its code commit. The manager verifies it and records the outcome in the brief's "Sessions".
- **Model and reasoning setting** (OD-10, OD-30, OD-33, OD-34, OD-42). The reading is the recommendation; it gates nothing, and Nathan picks.
  - **TypeSafe v8.2: Opus 5.5 at medium.** Effort score 1.10 (confidence 0.89); rung probabilities low 0.04, medium 0.83, high 0.13, extra high 0.00, max 0.00, ultracode 0.00. Model probabilities Fable 5.1 0.00, Opus 5.5 0.93, Sonnet 5.5 0.07, Haiku 5.5 0.00 (confidence 0.91). Twenty-four cells, computed from the two answers: Fable 5.1 at low 0.000, Fable 5.1 at medium 0.000, Fable 5.1 at high 0.000, Fable 5.1 at extra high 0.000, Fable 5.1 at max 0.000, Fable 5.1 at ultracode 0.000, Opus 5.5 at low 0.037, Opus 5.5 at medium 0.772, Opus 5.5 at high 0.121, Opus 5.5 at extra high 0.000, Opus 5.5 at max 0.000, Opus 5.5 at ultracode 0.000, Sonnet 5.5 at low 0.003, Sonnet 5.5 at medium 0.058, Sonnet 5.5 at high 0.009, Sonnet 5.5 at extra high 0.000, Sonnet 5.5 at max 0.000, Sonnet 5.5 at ultracode 0.000, Haiku 5.5 at low 0.000, Haiku 5.5 at medium 0.000, Haiku 5.5 at high 0.000, Haiku 5.5 at extra high 0.000, Haiku 5.5 at max 0.000, Haiku 5.5 at ultracode 0.000. Sent 2026-11-08T16:45:55Z. Nathan picks the cell.
- **The Dev Manager's read:** none before it runs (DM-43 1.4). C7 changes a test comment and the record, and authorizes no credential use and no live provider action.
- **Environment** (OD-36): `Glow App - No Stream`. No Stream variable is needed.
- **It runs alone** (OD-29). Codex's review of its head follows, then a delta review on DM-43 3.1 to 3.3.
- **Deletion condition:** prune after P06.2-F's PR merges and its merge receipt is recorded.

**Manager:** before giving this prompt to Nathan, replace every `<START_SHA>` with the full SHA of the manager-branch commit that holds this revision.

---

You are **correction C7 of P06.2-F**, the mobile hardening, for the Glow dating app, in the public repository `amthorn78/glow-dating-app`. Nathan Amthor, its owner, started you manually. This prompt is revision 1, from commit `<START_SHA>` of the manager branch `claude/magical-wozniak-yfmmx2`.

**What came before.**
- **The render-rule test** (`apps/mobile/src/chat/display-rule.test.ts`) checks from source that `src/chat/screen.tsx` and `src/chat/rows.ts` render only contract fields (ADR 0003). Its comment states, as a positive list, what the check refuses, what it is known to pass and what harmless code it refuses. The checks themselves are frozen (DM-39 1.1); only the comment's words change.
- **Correction C6** (code head `6913cc0`, integrated) replaced the comment's inline-callback sentence with DM-42's words, which state the places at which the inline rule (`:489-499`) compares a callback's parameters.
- **C6's delta review** found that at a rest parameter's place the rule compares the annotated parameter with the rest parameter's own type, the array `ConversationMessage[]`, not its element (`:495`, `checker.getTypeOfSymbol(given)`). So an annotation that declares only names an array also has passes (F-1: R1, `const lengthOf: (...entries: ConversationMessage[]) => string = (first: { at: string; length?: number }) => String(first.length ?? '')`), and a harmless annotation of the element type there is refused (H1). C6's sentence named the places but not the type compared at them. Codex found F-1 again.
- **The Dev Manager's DM-43** (read it whole) declined changing the check and approved words that name the compared type at each place, mapped clause by clause to the rule, with an R1 entry and an H1 entry. **Use its words exactly, or narrower ones, never wider.**

**What you do: DM-43's conditions, as written.** In them, "the next correction" means you, and "me" means the Dev Manager. 1.3's last bullet (the carried-items file) and 4.1 (the CI policy's count) are the manager's and already applied; you edit neither file. Line numbers are at `6913cc0`.

**Item 1 (DM-43 section 3.3):**

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

**The review that follows** (DM-43 section 4, for your information):

- **3.1 The next review's terms:** a delta review on DM-42 5.1 to 5.3's terms, limited to the changed words and the new entries, after Codex has completed on its code head and on the commit that holds its prompt (step 6). It is held to DM-39 1.2 for the changed text.
- **3.2 What it checks:**
  - each clause of 1.1 against the rule's lines at the new head (section 3.3's table, by content, since line numbers move);
  - that at least R1, R3, R4 and TU1 pass, and R2, R5, H1 and G1 are refused, for the reasons the words give;
  - the two new entries as written: R1's passes, and H1's fails as stated;
  - that only comments changed;
  - 4.1's line, word for word.
- **3.3 What it does not do:** it does not re-probe unchanged items. Other passing forms are records lines (DM-42 5.2). A form that fits inside the changed words and evades them comes to me first (DM-42 5.3).

**How you work:**
- Nathan started you and will relay your report to the manager, App Manager 10. You are neither the manager nor a reviewer.
- You may use any tools, subagents, scheduled wake-ups or other capabilities the work needs.
- **Your boundary is scope:**
  - **in the test file, change only the render-rule comment:** 1.1's sentence and 1.2's two entries. No refusal, exception, planted form, test name or other line changes (1.3);
  - **in the record** (`docs/testing/evidence/2026-11-01-p06-2-f-mobile-hardening.md`), add "## Correction C7" at the file's end, after "Delta review of correction C6", and change nothing else in it;
  - push only your own session branch, with `git push -u origin <branch>`. Never push `main`, the manager branch or `claude/dev-manager`, and never delete or force-push a branch;
  - on GitHub, read only: no pull request, comment, review, re-run, workflow dispatch or setting. Change nothing in Notion.
- **No words that claim coverage of code paths** (DM-38 4.2): never write "follows", "any", "every", "all" or "wherever" about what the check covers, in the comment or the record.
- **The stop rule:** stop and report, with no further change, if a word cannot be stated truly within DM-43's words or narrower ones, if anything seems to need a change outside the comment and the new section, or if you find a form that fits inside the changed words and evades them (DM-43 3.3).
- **Network:** the npm registry for `npm ci --ignore-scripts`, and GitHub through your tools to read your run. `npm ci` needs the proxy and certificate variable names passed through the clean environment by reference (C5's record); never print them.
- **Rendered tests:** C7 changes no rendered path; CI's run is the evidence. Never run `playwright install` here.
- **Never:**
  - dump the environment, or print, echo, log, copy or commit any credential, token or password, in any form;
  - call Stream or any other provider, or run any command in `proofs/stream-chat/`;
  - connect to any database, HDE, Railway or other external service;
  - run `playwright install`, `eas`, `eas-cli` or `migrate`;
  - run package install scripts: always `npm ci --ignore-scripts`.

## 1. Environment check (names only; never print values)

1. None of `DATABASE_URL`, `HD_API_KEY` or `GEO_API_KEY` may be set: `for n in DATABASE_URL HD_API_KEY GEO_API_KEY; do [ -n "${!n+x}" ] && echo "$n present"; done`. If any is present, stop and report.
2. **No `STREAM_*` name may be set:** `compgen -e | grep -E '^STREAM_'` prints names only. If any is present, stop and report.
3. **GitHub token names** may be present (`GITHUB_TOKEN`, `GH_TOKEN`). Never read them.
4. **The toolchain:** Node 24.19.0 and npm 11.9.0 in `$HOME/.local/bin`. Put it first on PATH yourself. Record their versions.
5. **A clean process environment** for every npm command: `env -i PATH="$HOME/.local/bin:$PATH" HOME="$HOME" LANG=C.UTF-8`, plus only the command's own variables.

## 2. Start gate

```bash
git fetch origin claude/magical-wozniak-yfmmx2 main
git switch -C <your session branch> <START_SHA>
git rev-parse HEAD                                  # must print <START_SHA>
git merge-base --is-ancestor <START_SHA> origin/claude/magical-wozniak-yfmmx2 && echo "this prompt's commit is on the live branch"
git diff --quiet 6913cc06822b6f26c185ea525ce3b3f28a3a5eca HEAD -- . ':(exclude)*.md' && echo "the code head under correction"
git diff --quiet 6913cc06822b6f26c185ea525ce3b3f28a3a5eca origin/claude/magical-wozniak-yfmmx2 -- . ':(exclude)*.md' && echo "no code on the live branch after 6913cc0"
git show origin/claude/magical-wozniak-yfmmx2:docs/testing/evidence/2026-11-01-p06-2-f-mobile-hardening.md | grep -c -E '^## Correction C7$'   # must print 0
```

If a check fails, stop and report. **Your branch name must match the push filter, `claude/**` or `ccr-**`.** If it does not, stop before pushing and report.

**Then read, completely:** root `AGENTS.md` and `CLAUDE.md`; `apps/mobile/AGENTS.md`; the brief's "Correction C6" and "Correction C7"; the record's "Correction C6" and "Delta review of correction C6"; DM-43's report, whole; `src/chat/display-rule.test.ts`, whole.

## 3. What to do

1. **The comment** (1.1, 1.2): replace and add as the conditions say. Check each quoted text against DM-43's report with a script, and record the result.
2. **Prove only comments changed** (1.3): `git diff 6913cc0 HEAD -- . ':(exclude)*.md'` touches only `display-rule.test.ts`, and both versions printed from their parse trees without comments are identical. Record how you checked.
3. **Check the new entries' examples** as real edits to `screen.tsx` in a scratch copy outside the checkout, with `type Loose = { name?: string; text: string | null }` where a form uses it: R1, R3 and R4 pass the test, `tsc` and ESLint; H1 fails as `a widening callback parameter: first: ConversationMessage`; restore the file and confirm its SHA-256.
4. **The local checks,** in `apps/mobile`: `npm ci --ignore-scripts`, then `npm run check` (at least 650 unit tests), and `node --test src/chat/display-rule.test.ts` 21 of 21.
5. **Push the code commit first,** then read its Foundation push run with your GitHub tools: every job's conclusion, the gate's line (`Application checks passed`), the unit and rendered counts, and whether any toolchain retry fired. **Push nothing else until that run has completed** (AM8-20). If the gate's line is not `Application checks passed`, stop and report.
6. **Then the record** (1.3): "Correction C7", with the words as the comment now carries them (naming any narrowing), DM-43's probe table cited and not repeated, your checks with their result lines, the run of record and what you could not run. Commit and push it.

Confirm that `git status` is clean and that `git diff --name-only <START_SHA> HEAD` lists only the two paths.

## 4. Report

Your final message is the report Nathan relays:
- the prompt revision (revision 1, from `<START_SHA>`), your branch, code head and records head;
- the start gate's and the environment check's results;
- the script's result for each quoted text, and any narrowing, with why;
- how you showed that only comments changed;
- R1, R3, R4 and H1's results;
- the local checks' results;
- the run of record (ID, every job, the gate's line, the unit and rendered counts, whether a retry fired);
- anything that met the stop rule, and what you could not run.
