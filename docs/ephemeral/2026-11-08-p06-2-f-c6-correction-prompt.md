# P06.2-F correction C6 prompt — the inline rule's pairing, stated as written (DM-42)

- **Owner:** App Manager 10. Nathan starts this session manually, in the `Glow App - No Stream` environment (OD-36), and relays its report.
- **Revision 1, 8 November 2026.** Corrected before it was given (the same revision): items 2 and 3 and the review's section now carry DM-42's text whole, without its section heading.
- **Durable brief:** [P06.2-F — Mobile hardening and P06.2's carried follow-ups](../planning/p06-2-f-mobile-hardening.md), revision 6, its section "Correction C6". The design is [DM-42](../continuity/dev-manager/reviews/2026-11-08-dm-42-p06-2-f-c5-review-findings.md), sections 1, 3 and 4.
- **Where the result goes:** the session's change to the render-rule comment in `apps/mobile/src/chat/display-rule.test.ts`, and the record's new "Correction C6" section, on its own branch; the run of record, the Foundation push run on its code commit. The manager verifies it and records the outcome in the brief's "Sessions".
- **Model and reasoning setting** (OD-10, OD-30, OD-33, OD-34, OD-42). The reading is the recommendation; it gates nothing, and Nathan picks.
  - **TypeSafe v8.2: Opus 5.5 at medium.** Effort score 1.24 (confidence 0.81); rung probabilities low 0.02, medium 0.73, high 0.24, extra high 0.01, max 0.00, ultracode 0.00. Model probabilities Fable 5.1 0.00, Opus 5.5 0.87, Sonnet 5.5 0.10, Haiku 5.5 0.03 (confidence 0.83). Twenty-four cells, computed from the two answers: Fable 5.1 at low 0.000, Fable 5.1 at medium 0.000, Fable 5.1 at high 0.000, Fable 5.1 at extra high 0.000, Fable 5.1 at max 0.000, Fable 5.1 at ultracode 0.000, Opus 5.5 at low 0.017, Opus 5.5 at medium 0.635, Opus 5.5 at high 0.209, Opus 5.5 at extra high 0.009, Opus 5.5 at max 0.000, Opus 5.5 at ultracode 0.000, Sonnet 5.5 at low 0.002, Sonnet 5.5 at medium 0.073, Sonnet 5.5 at high 0.024, Sonnet 5.5 at extra high 0.001, Sonnet 5.5 at max 0.000, Sonnet 5.5 at ultracode 0.000, Haiku 5.5 at low 0.001, Haiku 5.5 at medium 0.022, Haiku 5.5 at high 0.007, Haiku 5.5 at extra high 0.000, Haiku 5.5 at max 0.000, Haiku 5.5 at ultracode 0.000. Sent 2026-11-08T14:35:07Z. Nathan picks the cell.
- **The Dev Manager's read:** none before it runs (DM-42 1.4). C6 changes a test comment and the record, and authorizes no credential use and no live provider action.
- **Environment** (OD-36): `Glow App - No Stream`. No Stream variable is needed.
- **It runs alone** (OD-29). Codex's review of its head follows, then a delta review on DM-42 5.1 to 5.3.
- **Deletion condition:** prune after P06.2-F's PR merges and its merge receipt is recorded.

**Manager:** before giving this prompt to Nathan, replace every `<START_SHA>` with the full SHA of the manager-branch commit that holds this revision.

---

You are **correction C6 of P06.2-F**, the mobile hardening, for the Glow dating app, in the public repository `amthorn78/glow-dating-app`. Nathan Amthor, its owner, started you manually. This prompt is revision 1, from commit `<START_SHA>` of the manager branch `claude/magical-wozniak-yfmmx2`.

**What came before.**
- **The render-rule test** (`apps/mobile/src/chat/display-rule.test.ts`) checks from source that `src/chat/screen.tsx` and `src/chat/rows.ts` render only contract fields (ADR 0003). Its comment states, as a positive list, what the check refuses and what it is known to pass. The checks themselves are frozen (DM-39 1.1); only the comment's words change.
- **Correction C4** narrowed the comment to DM-40's words; **repair pass C5** (code head `7f1df96`) fixed a rendered race and the CI retry and is integrated.
- **The review of C4 and C5** found two forms inside C4's inline-callback sentence that pass the test: a function expression with a declared `this` parameter, and a parameter after a rest parameter of the contextual signature. The inline rule (`:476-486`) pairs `node.parameters[index]` with `signature.parameters[index]`; a declared `this` is in the first list only, and a signature's rest parameter is one entry. Codex found both again.
- **The Dev Manager's DM-42** (read it whole) declined changing the check and approved new words that state the pairing as written, with the forms (and a third, F3) named as known passing classes. **Use its words exactly, or narrower ones, never wider.**

**What you do: DM-42's conditions, as written.** In them, "the next correction" means you, and "me" means the Dev Manager. 1.3's last bullet (the carried-items file) and 4.1 (the CI policy line) are the manager's and already applied; you edit neither file. Line numbers are at `7f1df96`.

**Item 1 (DM-42 section 3.2):**

- **1.1 The callback item.** The next correction replaces "An inline arrow function or function expression is compared at each parameter that has a type annotation, against its contextual signature [15]; what it returns is checked as a widening (above)." (`7f1df96`, `:166-168`) with:

  > An inline arrow function or function expression that has a contextual type is compared at each parameter that has a type annotation, against the parameter in the same place in each call signature of that type (of each member, for a union). Places are counted as written: a declared `this` takes the first place in the function's list and none in the signature's, and a rest parameter of the signature takes one place; a parameter with no parameter in its place is not compared [15]. What it returns is checked as a widening (above).

  The rest of the item stays as it is. The next correction may narrow these words, never widen them.
- **1.2 Two known-passing entries,** added in the list's style:
  - **A function expression with a declared `this` parameter** (the review of C4 and C5, finding 1): `[message].map(function (this: ConversationMessage, entry: Loose) { return entry.name ?? ''; })`, where `entry` is compared against the signature's second place, `index`. The same holds for a declared `this` when the contextual signature has no parameter in the first place: `const viaThis: (this: ConversationMessage) => string = function (this: Loose) { return this.name ?? ''; }`, then `viaThis.call(message)` (DM-42).
  - **A parameter after a rest parameter of the contextual signature** (finding 2): `const join: (...entries: ConversationMessage[]) => string = (first, second: Loose) => second.name ?? String(first.text)`, then `join(message, message)`.
- **1.3 Scope:**
  - In the test file, only comments change. No refusal, exception, planted form or other line changes. The parse trees without comments stay identical to `7f1df96`'s.
  - The record's new section states the words as applied, with this report's probe table cited, not repeated.
  - The manager adds to (c)'s inputs in the carried-items file: F1, F2 and F3, with the fix noted and not made: "pair a declared `this` with the contextual signature's `this`, and each later parameter through `parameterAt`, as the by-reference rule does".
- **1.4 The prompt:**
  - It changes a test comment and the record, and authorizes no credential use or live provider action. So no Dev Manager read is needed before it runs, as with C4 (DM-40 4.2).
  - It states 1.1 to 1.3, 2.1, 3.1 and 5.1 to 5.3 as written. My next consultation confirms that it did.


**Items 2 and 3 (DM-42 section 4):**

- **2.1 Finding 3 is valid.** At `7f1df96`:
  - `every` occurs at `:185` (the method's name, among the named exceptions);
  - "Every" begins two code comments (`:105`, `:721`);
  - "wherever" is in a code comment (`:511`).

  None claims coverage of code paths. The next correction appends this line to its own record section:

  > **A correction to "Correction C4 (written by repair pass C5)"** (the review of C4 and C5, finding 3). Its sentence ""follows", "wherever" and "every" do not occur in the comments" is not so. At `7f1df96`, `every` occurs at `:185` (the method's name, among the named exceptions), "Every" begins two code comments (`:105`, `:721`), and "wherever" is in a code comment (`:511`). None claims coverage of code paths, so DM-38 4.2 holds.
- **3.1 Finding 4 is valid** (V1 to V3): `data` is reported as a widening to `unknown` in each form, and `any` appears only where `getItem` returns Glow's data. In V1, `getItem`'s `data[index]` reads an `any` and is reported as a computed read.

  The next correction replaces "A `VirtualizedList`, whose `data` prop is typed `any`, fails as a widening to `unknown` and to `any`." (`:240-242`) with:

  > A `VirtualizedList` over the messages fails as a widening to `unknown` at its `data` prop, and as a widening to `any` where its `getItem` returns Glow's data.

  It no longer states the prop's declared type, which depends on which of React Native's declaration files the program resolves.

**The review that follows** (DM-42 section 5, for your information):

**Agreed:** a delta review on S2's terms of the next correction's code head, after Codex has completed on that head and on the commit that holds its prompt (step 6), held to DM-39 1.2 for the text that changes.

- **5.1 What it checks:**
  - the callback sentence against the inline rule (`:476-486`), place by place;
  - that F1, F2 and F3 pass as written;
  - that at least F4, F5, F7 and F8 are refused, as the words say;
  - finding 4's line, against V1 to V3 or its own forms;
  - finding 3's correction line;
  - that the parse trees without comments are identical to `7f1df96`'s, so only comments changed;
  - the CI line, if it has been applied.
- **5.2 What it does not do:** it does not re-probe unchanged items. Any other passing form is a records line, carried to (c)'s inputs, not a finding (DM-40 3.3).
- **5.3 What still comes to me first:** a form that fits inside the new callback sentence and evades it, before any further correction (DM-40 3.4).

**How you work:**
- Nathan started you and will relay your report to the manager, App Manager 10. You are neither the manager nor a reviewer.
- You may use any tools, subagents, scheduled wake-ups or other capabilities the work needs.
- **Your boundary is scope:**
  - **in the test file, change only the render-rule comment:** 1.1's sentence, 1.2's two entries and 3.1's sentence. No refusal, exception, planted form, test name or other line changes (1.3);
  - **in the record** (`docs/testing/evidence/2026-11-01-p06-2-f-mobile-hardening.md`), add "## Correction C6" at the file's end, after "Review of C4 and repair pass C5" and its dispositions, and change nothing else in it;
  - push only your own session branch, with `git push -u origin <branch>`. Never push `main`, the manager branch or `claude/dev-manager`, and never delete or force-push a branch;
  - on GitHub, read only: no pull request, comment, review, re-run, workflow dispatch or setting. Change nothing in Notion.
- **No words that claim coverage of code paths** (DM-38 4.2): never write "follows", "any", "every", "all" or "wherever" about what the check covers, in the comment or the record.
- **The stop rule:** stop and report, with no further change, if a word cannot be stated truly within DM-42's words or narrower ones, if anything seems to need a change outside the comment and the new section, or if you find a form that fits inside the new callback sentence and evades it (DM-42 5.3).
- **Network:** the npm registry for `npm ci --ignore-scripts`, and GitHub through your tools to read your run. `npm ci` needs the proxy and certificate variable names passed through the clean environment by reference (C5's record); never print them.
- **Rendered tests:** C6 changes no rendered path; CI's run is the evidence. Never run `playwright install` here.
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
git diff --quiet 7f1df9615b10e844dc252b9111b3c4c5b67b0b37 HEAD -- . ':(exclude)*.md' && echo "the code head under correction"
git diff --quiet 7f1df9615b10e844dc252b9111b3c4c5b67b0b37 origin/claude/magical-wozniak-yfmmx2 -- . ':(exclude)*.md' && echo "no code on the live branch after 7f1df96"
git show origin/claude/magical-wozniak-yfmmx2:docs/testing/evidence/2026-11-01-p06-2-f-mobile-hardening.md | grep -c -E '^## Correction C6$'   # must print 0
```

If a check fails, stop and report. **Your branch name must match the push filter, `claude/**` or `ccr-**`.** If it does not, stop before pushing and report.

**Then read, completely:** root `AGENTS.md` and `CLAUDE.md`; `apps/mobile/AGENTS.md`; the brief's "Correction C4" and "Correction C6"; the record's "Correction C4 (written by repair pass C5)" and "Review of C4 and repair pass C5", with its dispositions; DM-42's report, whole; `src/chat/display-rule.test.ts`, whole.

## 3. What to do

1. **The comment** (1.1, 1.2, 3.1): replace and add as the conditions say. Check each quoted text against DM-42's report with a script, and record the result.
2. **Prove only comments changed** (1.3): `git diff 7f1df96 HEAD -- . ':(exclude)*.md'` touches only `display-rule.test.ts`, and both versions printed from their parse trees without comments are identical. Record how you checked.
3. **Check the new entries' examples** as real edits to `screen.tsx` in a scratch copy outside the checkout, with `type Loose = { name?: string; text: string | null }`: F1, F2 and F3 pass the test, `tsc` and ESLint; restore the file and confirm its SHA-256.
4. **The local checks,** in `apps/mobile`: `npm ci --ignore-scripts`, then `npm run check` (at least 650 unit tests), and `node --test src/chat/display-rule.test.ts` 21 of 21.
5. **Push the code commit first,** then read its Foundation push run with your GitHub tools: every job's conclusion, the gate's line (`Application checks passed`), the unit and rendered counts, and whether any toolchain retry fired. **Push nothing else until that run has completed** (AM8-20). If the gate's line is not `Application checks passed`, stop and report.
6. **Then the record** (1.3, 2.1): "Correction C6", with the words as the comment now carries them (naming any narrowing), DM-42's probe table cited and not repeated, DM-42 2.1's correction line, your checks with their result lines, the run of record and what you could not run. Commit and push it.

Confirm that `git status` is clean and that `git diff --name-only <START_SHA> HEAD` lists only the two paths.

## 4. Report

Your final message is the report Nathan relays:
- the prompt revision (revision 1, from `<START_SHA>`), your branch, code head and records head;
- the start gate's and the environment check's results;
- the script's result for each quoted text, and any narrowing, with why;
- how you showed that only comments changed;
- F1 to F3's results;
- the local checks' results;
- the run of record (ID, every job, the gate's line, the unit and rendered counts, whether a retry fired);
- anything that met the stop rule, and what you could not run.
