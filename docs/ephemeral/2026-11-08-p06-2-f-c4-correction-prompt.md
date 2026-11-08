# P06.2-F correction C4 prompt — the listed items narrowed to the syntax the check refuses (DM-40)

- **Owner:** App Manager 9. Nathan starts this session manually, in the `Glow App - No Stream` environment (OD-36), and relays its report.
- **Revision 1, 8 November 2026.**
- **Durable brief:** [P06.2-F — Mobile hardening and P06.2's carried follow-ups](../planning/p06-2-f-mobile-hardening.md), revision 4, its section "Correction C4". The design is [DM-40](../continuity/dev-manager/reviews/2026-11-08-dm-40-p06-2-f-c3-review-and-od-57.md), sections 4 and 6.
- **Where the result goes:** the session's change to the render-rule comment and the first render test's name in `apps/mobile/src/chat/display-rule.test.ts`, and the record's new "Correction C4" section, on its own branch; the run of record, the Foundation push run on its code commit. The manager verifies it and records the outcome in the brief's "Sessions".
- **Model and reasoning setting** (OD-10, OD-30, OD-33, OD-34, OD-42). The reading is the recommendation; it gates nothing, and Nathan picks.
  - **TypeSafe v8.2: Opus 5.5 at medium.** Effort score 1.11 (confidence 0.88); rung probabilities low 0.04, medium 0.82, high 0.14, extra high 0.00, max 0.00, ultracode 0.00. Model probabilities Fable 5.1 0.00, Opus 5.5 0.91, Sonnet 5.5 0.08, Haiku 5.5 0.01 (confidence 0.88). Twenty-four cells, computed from the two answers: Fable 5.1 at low 0.000, Fable 5.1 at medium 0.000, Fable 5.1 at high 0.000, Fable 5.1 at extra high 0.000, Fable 5.1 at max 0.000, Fable 5.1 at ultracode 0.000, Opus 5.5 at low 0.036, Opus 5.5 at medium 0.746, Opus 5.5 at high 0.127, Opus 5.5 at extra high 0.000, Opus 5.5 at max 0.000, Opus 5.5 at ultracode 0.000, Sonnet 5.5 at low 0.003, Sonnet 5.5 at medium 0.066, Sonnet 5.5 at high 0.011, Sonnet 5.5 at extra high 0.000, Sonnet 5.5 at max 0.000, Sonnet 5.5 at ultracode 0.000, Haiku 5.5 at low 0.000, Haiku 5.5 at medium 0.008, Haiku 5.5 at high 0.001, Haiku 5.5 at extra high 0.000, Haiku 5.5 at max 0.000, Haiku 5.5 at ultracode 0.000. Sent 2026-11-08T07:52:08Z. Nathan picks the cell.
- **The Dev Manager's read:** none before it runs (DM-40 section 4.2). C4 changes a test comment, one test name and the record. This prompt authorizes no credential use and no live provider action.
- **Environment** (OD-36): `Glow App - No Stream`. No Stream variable is needed.
- **It runs alone** (OD-29). Codex's review of its head follows, then a delta re-review bounded to the changed items (DM-40 3.1 to 3.4).
- **Deletion condition:** prune after P06.2-F's PR merges and its merge receipt is recorded.

**Manager:** before giving this prompt to Nathan, replace every `<START_SHA>` with the full SHA of the manager-branch commit that holds this revision.

---

You are **correction C4 of P06.2-F**, the mobile hardening, for the Glow dating app, in the public repository `amthorn78/glow-dating-app`. Nathan Amthor, its owner, started you manually. This prompt is revision 1, from commit `<START_SHA>` of the manager branch `claude/magical-wozniak-yfmmx2`.

**What came before.**
- **The render-rule test** (`src/chat/display-rule.test.ts`) checks from source that `src/chat/screen.tsx` and `src/chat/rows.ts` render only contract fields, never a provider-shaped one (ADR 0003). Its comment states, under DM-39, what the check refuses, as a positive list, with the forms it is known to pass.
- **Correction C3** (code head `f87e8b1`) wrote that comment. **Its delta re-review** found three forms that evade refusals the comment lists, and two false statements (the record, "Delta re-review of correction C3"):
  - an object literal's method shorthand;
  - a contextually typed parameter's destructuring default;
  - a destructuring target in a `for…of` head;
  - more text-match misses in the source check than the four named;
  - a wrong reason for `VirtualizedList`.
- **The Dev Manager's DM-40** decided that the checks stay as they are, and the comment's items are narrowed to the syntax the check refuses, with the forms named as known passing classes. Its section 4.2 gives the words. Its probes showed that wording by category, rather than by syntax, still covers forms that pass, so **use its words exactly, or narrower ones, and never wider** (DM-40 1.2).

**What you do** is the brief's "Correction C4", Outcome 1 to 5. Each item below replaces the text named; line numbers are at `f87e8b1`.

1. **The source check's last sentence** (`:124-126`, from "As a text match it passes" to "refuses each of them."):

   > As a text match, spacing, line breaks, parentheses, comments, string contents and bracket forms evade it, for example `message ?.name`, `(message)as{…}`, `'name'in message`, `'/*'` in a string and `Reflect['get']`; C3's verifiers and its delta re-review found these, and the type check refuses each one tried.

   A string containing `/*` or `*/` inside the comment itself must not break the comment block: check that the file still parses and the test still passes.
2. **The destructuring assignment** (`:155`): "a destructuring assignment" becomes "a destructuring assignment written with `=`".
3. **The callback item** (`:162-165`, the whole item from "a callback, inline or passed by reference" to its bracket):

   > a callback whose parameter widens what it is given, or whose return of Glow's data is widened. An inline arrow function or function expression is compared at each parameter that has a type annotation, against its contextual signature [15]; what it returns is checked as a widening (above). Any other expression whose type has a call signature (a function's name, a `useCallback` result, a property read such as `view.line`) is compared at each parameter and at its return, against the call's resolved parameter or its contextual type [C2-1a to C2-1e]. An object literal property written `key: value` or `{ key }`, in a literal that has a contextual type, is compared by these two rules [no planted form]. A function reached only through an object or a class instance is not compared (below).

4. **`Reflect` and `Object` by a destructuring** (`:170-172`): "by a destructuring's type, whatever its key" becomes:

   > by a destructuring whose type is `Reflect` or `ObjectConstructor`, as a string or computed key that names one gives [C2-3c, C2-3d]; a key of a union type gives a union, which is not refused (O5)

   Keep the item's other brackets (C2-3a and C2-3b) as they are.
5. **The destructuring exception** (`:178-179`, from "the initializer of an object destructuring" to "C2-4b pins it)"):

   > the initializer of an object destructuring when no enclosing pattern is annotated (C2: only then; C2-4b pins it). The pattern's own check reads the initializer's fields only when the pattern is typed as Glow's data, as when the initializer types it. When the pattern's type comes from context, as for an unannotated parameter of a contextually typed function, the initializer is exempt and not checked (below).

6. **F0's family** (`:212-217`, from "and so do a `VirtualizedList`" to "as widenings;"):

   > …and so do `Array.from` and `new Set` over the messages, since the check reads an `ArrayLike` parameter's index signature, and an `Iterable` parameter's symbol-keyed iterator, which it does not find by name on the array, as widenings. A `VirtualizedList`, whose `data` prop is typed `any`, fails as a widening to `unknown` and to `any`.

   The "…" stands for the sentence's start, which stays as it is.
7. **"What it is known to pass" gains four entries**, in the list's style (`Loose` is already defined there):
   - **A function reached only through an object or class instance** (C3's delta re-review, finding 1): `const view: { line(entry: ConversationMessage): string } = { line(entry: Loose) { return entry.name ?? ''; } }`, then `view.line(message)`. The same holds for an accessor, for a class's method or field under an interface type, and for an object literal with no contextual type that is given later.
   - **A contextually typed parameter's destructuring default** (finding 2): `const caption: (entry?: Loose) => string = ({ name } = message) => name ?? ''`.
   - **A destructuring target in a `for…of` head** (finding 3): `for ({ ...rest } of conversation.messages) break;`.
   - **A reflective global reached through a key of a union type** (O5): `globalThis[key]`, with `key: 'Reflect' | 'JSON'`. No read through it was found.
8. **The first render test's name** (`:670`): `the chat screens render only the contract's fields: no provider-shaped field is read, whatever the validators let through (M05 finding 18)` becomes `today's chat screens and list rows pass both render-rule checks (M05 finding 18)`. Keep the string's quoting valid.

DM-39's core paragraph and every other item stay as they are. You may make an item narrower than its words, never wider; if you narrow one, say which and why in the record.

**How you work:**
- Nathan started you and will relay your report to the manager, App Manager 9. You are neither the manager nor a reviewer.
- You may use any tools, subagents, scheduled wake-ups or other capabilities the work needs.
- **Your boundary is scope:**
  - **In the test file, change only the render-rule comment and the first render test's name.** No refusal, exception, planted form or other line changes (DM-40 1.1);
  - **in the record,** add "Correction C4" after the section "Delta re-review of correction C3" (at the file's end, after its dispositions), and change nothing else in it;
  - push only your own session branch, with `git push -u origin <branch>`. Never push `main`, the manager branch or `claude/dev-manager`, and never delete or force-push a branch;
  - on GitHub, read only: no pull request, comment, review, re-run, workflow dispatch or setting. Change nothing in Notion.
- **No words that claim coverage of code paths** (DM-38 4.2): never write "follows", "any", "every", "all" or "wherever" about what the check covers, in the comment or the record.
- **The stop rule:** stop and report, with no further change, if an item cannot be stated truly within DM-40's words or narrower ones, or if anything seems to need a change outside the comment, the test name and the new section, or a dependency.
- **Network:** none beyond the npm registry for `npm ci --ignore-scripts`.
- **Rendered tests:** C4 changes no rendered path; CI's run is the evidence. Never run `playwright install` here: this is a cloud container (OD-57).
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
4. **The toolchain:** Node 24.19.0 and npm 11.9.0 in `$HOME/.local/bin`. Put it first on PATH yourself (C3 found another directory before it). Record their versions.
5. **A clean process environment** for every npm command: `env -i PATH="$HOME/.local/bin:$PATH" HOME="$HOME" LANG=C.UTF-8`, plus only the command's own variables.

## 2. Start gate

```bash
git fetch origin claude/magical-wozniak-yfmmx2 main
git switch -C <your session branch> <START_SHA>
git rev-parse HEAD                                  # must print <START_SHA>
git merge-base --is-ancestor <START_SHA> origin/claude/magical-wozniak-yfmmx2 && echo "this prompt's commit is on the live branch"
git diff --quiet f87e8b19110544b1ceddfc1afd44a8492350fb81 HEAD -- .github scripts services apps packages proofs ':(exclude)*.md' && echo "the code head under correction"
git diff --quiet f87e8b19110544b1ceddfc1afd44a8492350fb81 origin/claude/magical-wozniak-yfmmx2 -- .github scripts services apps packages proofs ':(exclude)*.md' && echo "no code on the live branch after f87e8b1"
git show origin/claude/magical-wozniak-yfmmx2:docs/testing/evidence/2026-11-01-p06-2-f-mobile-hardening.md | grep -c -E '^#+ Correction C4'   # must print 0
```

If a check fails, stop and report.

**Then read, completely:** root `AGENTS.md` and `CLAUDE.md`; `apps/mobile/AGENTS.md`; the brief's "Correction C3" and "Correction C4"; the record's "Correction C2" (its N1 to N9 table and the forms' IDs), "Correction C3", "Manager verification of correction C3" and "Delta re-review of correction C3", with its dispositions; DM-40's report, whole (`docs/continuity/dev-manager/reviews/2026-11-08-dm-40-p06-2-f-c3-review-and-od-57.md`); `src/chat/display-rule.test.ts`, whole.

## 3. What to do

1. **The comment and the test name** (Outcome 1 and 2): items 1 to 8 above. Check each quoted item against DM-40 section 4.2's text with a script, and record the result.
2. **Prove nothing else changed** (Outcome 3): `git diff f87e8b19110544b1ceddfc1afd44a8492350fb81 HEAD -- apps` touches only `display-rule.test.ts`. Show that both versions, printed from their parse trees without comments, are identical except for the test name's string (for example, by replacing that one string literal in both before comparing), and record how you checked.
3. **Check each new known-passing example** as a real edit to `screen.tsx` in a scratch copy outside the checkout: it passes the test, `tsc` and ESLint, and the file's SHA-256 matches after you restore it.
4. **The local checks,** in `apps/mobile`: `npm ci --ignore-scripts`, then `npm run check`; the test count must be at least 650, and `node --test src/chat/display-rule.test.ts` 21 of 21.
5. **Push the code commit first,** then read its Foundation push run with your GitHub tools: every job's conclusion, the gate's line (`Application checks passed`), the `@glow/mobile` unit count, the rendered count and the Mobile job's duration. **Push nothing else until that run has completed** (AM8-20). If the gate's line is not `Application checks passed`, stop and report.
6. **Then the record** (Outcome 5): "Correction C4" after "Delta re-review of correction C3", with:
   - DM-40 section 4.2's words as the comment now carries them, and the new test name;
   - a line saying that it supersedes C3's items named above without editing them;
   - nits 6 and 7: C2's forms by class and ID, the duplicate IDs named (`R3` is "now caught" in one row and listed under N3; `R6` is in N4 and among the caught by-reference forms), and the 49th form placed in N4 or N5 (C2's mechanism table's "passed" row);
   - DM-40 1.3's forms, for option (c)'s inputs: the review's findings 1 to 4 and O5, and DM-40 section 3's F1c (an accessor), F1d (a class instance), G2 (an untyped literal given later) and G3 (a class field);
   - the start gate, the environment check (names only), every command with its result line, the run of record, and what you could not run.

   Commit and push it.

Confirm that `git status` is clean and that `git diff --name-only <START_SHA> HEAD` lists only the two paths.

## 4. Report

Your final message is the report Nathan relays:
- the prompt revision (revision 1, from `<START_SHA>`), your branch, code head and records head;
- the start gate's and the environment check's results;
- the script's result for each quoted item, and any item you narrowed, with why;
- how you showed that only the comment and the test name changed;
- each new example's result;
- `npm run check`'s result and count;
- the run of record (ID, every job, the gate's line, the unit and rendered counts, Mobile's duration);
- anything that met the stop rule, and what you could not run.
