# P06.2-F correction C2 prompt — the render-rule check's guarantee, after DM-38

- **Owner:** App Manager 9. Nathan starts this session manually, in the `Glow App - No Stream` environment (OD-36), and relays its report.
- **Revision 1, 2 November 2026.**
- **Durable brief:** [P06.2-F — Mobile hardening and P06.2's carried follow-ups](../planning/p06-2-f-mobile-hardening.md), revision 2, its section "Correction C2". The findings are in the record, [`docs/testing/evidence/2026-11-01-p06-2-f-mobile-hardening.md`](../testing/evidence/2026-11-01-p06-2-f-mobile-hardening.md), "Delta re-review of correction C1"; the design is [DM-38](../continuity/dev-manager/reviews/2026-11-02-dm-38-p06-2-f-render-rule-check.md).
- **Where the result goes:** the session's change to `apps/mobile/src/chat/display-rule.test.ts` and its record's new "Correction C2" section, on its own branch; the run of record, the Foundation push run on its code commit. The manager verifies it and records the outcome in the brief's "Sessions".
- **Model and reasoning setting** (OD-10, OD-30, OD-33, OD-34, OD-42). The reading is the recommendation; it gates nothing, and Nathan picks.
  - **TypeSafe v8.2: Opus 5.5 at high.** Effort score 2.03 (confidence 0.91); rung probabilities low 0.00, medium 0.05, high 0.87, extra high 0.08, max 0.00, ultracode 0.00. Model probabilities Fable 5.1 0.00, Opus 5.5 1.00, Sonnet 5.5 0.00, Haiku 5.5 0.00 (confidence 1.00). Twenty-four cells, computed from the two answers: Fable 5.1 at low 0.000, Fable 5.1 at medium 0.000, Fable 5.1 at high 0.000, Fable 5.1 at extra high 0.000, Fable 5.1 at max 0.000, Fable 5.1 at ultracode 0.000, Opus 5.5 at low 0.000, Opus 5.5 at medium 0.050, Opus 5.5 at high 0.870, Opus 5.5 at extra high 0.080, Opus 5.5 at max 0.000, Opus 5.5 at ultracode 0.000, Sonnet 5.5 at low 0.000, Sonnet 5.5 at medium 0.000, Sonnet 5.5 at high 0.000, Sonnet 5.5 at extra high 0.000, Sonnet 5.5 at max 0.000, Sonnet 5.5 at ultracode 0.000, Haiku 5.5 at low 0.000, Haiku 5.5 at medium 0.000, Haiku 5.5 at high 0.000, Haiku 5.5 at extra high 0.000, Haiku 5.5 at max 0.000, Haiku 5.5 at ultracode 0.000. Sent 2026-11-02T18:23:21Z. Nathan picks the cell.
- **The Dev Manager's read:** none before it runs (DM-38 item 3). C2 applies DM-38's conditions within the design it approved, and changes no runtime code, guard, contract, dependency or interface. This prompt authorizes no credential use and no live provider action.
- **Environment** (OD-36): `Glow App - No Stream`. No Stream variable is needed.
- **It runs alone** (OD-29). Codex's review of its head follows, then a delta re-review.
- **Deletion condition:** prune after P06.2-F's PR merges and its merge receipt is recorded.

**Manager:** before giving this prompt to Nathan, replace every `<START_SHA>` with the full SHA of the manager-branch commit that holds this revision.

---

You are **correction C2 of P06.2-F**, the mobile hardening, for the Glow dating app, in the public repository `amthorn78/glow-dating-app`. Nathan Amthor, its owner, started you manually. This prompt is revision 1, from commit `<START_SHA>` of the manager branch `claude/magical-wozniak-yfmmx2`.

**What came before.**
- **P06.2-F's item 2** made the chat screens' render rule rest on more than the client validator: `src/chat/display-rule.test.ts` checks from source that `src/chat/screen.tsx` and `src/chat/rows.ts` render only contract fields, never a provider-shaped one (ADR 0003).
- **Correction C1** (code head `0881db5`) kept the old source check and added a type check on the installed TypeScript compiler that finds Glow's data by its type, with 22 planted forms, each failing for a named reason. The record's "Correction C1" describes it.
- **C1's delta re-review asked for changes** (the record, "Delta re-review of correction C1"). The type check tracks Glow's data only by the value's own type, so these let a provider-shaped field through while passing the test, `tsc` and ESLint:
  - **finding 1:** data held inside another value: a wrapper, a closure, a container;
  - **finding 2:** a function passed by reference, such as `[message].map(shout)`;
  - **finding 3:** a local type guard; aliased `Reflect` or `Object.assign`;
  - **finding 4:** two exceptions wider than they say;
  - **finding 5:** the record's "through any binding" claims more than that;
  - **nits 6 to 8.**
- **The Dev Manager's DM-38** approved the fix's design: option (b) with conditions 2.1 to 2.6.
  - C2 fixes findings 2 to 5.
  - **Finding 1 is not fixed:** it becomes a named limit that an ordinary refactor reaches. A later change to how the screens hold data is to move them to view models instead (carried; not yours).
  - **The guarantee,** in DM-38 section 4's words, which you put in the test comment and the record:

  > The check follows Glow's data by its own type: at a property read, a destructuring, a spread, an enumeration and an `in` check, and wherever the data is passed, returned, assigned, annotated, given as a prop, or given to a callback, inline or by reference. It refuses type predicates and assertion signatures, references to `Reflect` and to `Object` members other than `freeze` however aliased, and any type error. It does not follow data held inside another value (a group or section, a list's render-item wrapper, a view-model object, a closure or a container), another module, or a template literal's coercion. It refuses some harmless code, such as a list component over Glow's data. It is a test over two files' source, not a proof over all programs.

**What you do** is the brief's "Correction C2", Outcome 1 to 7. Follow it, and read DM-38 sections 3 to 5, whose probes (F0 to F6) and throwaway change for 2.1 (about twelve lines) are the starting point.

**How you work:**
- Nathan started you and will relay your report to the manager, App Manager 9. You are neither the manager nor a reviewer.
- You may use any tools, subagents, scheduled wake-ups or other capabilities the work needs.
- **Your boundary is scope:**
  - write only `apps/mobile/src/chat/display-rule.test.ts` and the record `docs/testing/evidence/2026-11-01-p06-2-f-mobile-hardening.md`. In the record, change only the session sections (the "Correction C1" Mobile row, nit 8), and add "Correction C2" after "Delta re-review of correction C1". Never edit "Manager verification", "Exact-head review of P06.2-F", "Manager verification of correction C1" or "Delta re-review of correction C1";
  - push only your own session branch, with `git push -u origin <branch>`. Never push `main`, the manager branch or `claude/dev-manager`, and never delete or force-push a branch;
  - on GitHub, read only: no pull request, comment, review, re-run, workflow dispatch or setting. Change nothing in Notion.
- **The stop rule** (DM-38 2.1). Stop and report, with no further change, if any of these holds:
  - an item cannot pass today's `screen.tsx` and `rows.ts` without a new exception. No exception is added without the Dev Manager;
  - an item seems to need a change to `screen.tsx`, `rows.ts` or any path outside the two above;
  - it seems to need a dependency or a lock change (`typescript` is already a devDependency and may be imported by the test).
- **Claims:** the record states the guarantee and its limits. Never write that the check catches a field "through any binding", in "every" or "all" forms, or that a form "cannot" pass. Name the forms you tested and the limits that remain (DM-38 4.2).
- **Network:** none beyond the npm registry for `npm ci --ignore-scripts`.
- **Never:**
  - dump the environment, or print, echo, log, copy or commit any credential, token or password, in any form;
  - call Stream or any other provider, or run any command in `proofs/stream-chat/`;
  - connect to any database, HDE, Railway or other external service;
  - run `playwright install`, `eas`, `eas-cli` or `migrate`;
  - run package install scripts: always `npm ci --ignore-scripts`;
  - weaken or delete a test or a planted form to make the suite pass.

## 1. Environment check (names only; never print values)

1. None of `DATABASE_URL`, `HD_API_KEY` or `GEO_API_KEY` may be set: `for n in DATABASE_URL HD_API_KEY GEO_API_KEY; do [ -n "${!n+x}" ] && echo "$n present"; done`. If any is present, stop and report.
2. **No `STREAM_*` name may be set:** `compgen -e | grep -E '^STREAM_'` prints names only. If any is present, stop and report: this session must start in `Glow App - No Stream`.
3. **GitHub token names** may be present (`GITHUB_TOKEN`, `GH_TOKEN`). Never read them; every command below runs without them.
4. **The toolchain:** Node 24.19.0 and npm 11.9.0 in `$HOME/.local/bin`, first on PATH in every process. Record `node --version` and `npm --version`.
5. **A clean process environment** for every npm and Expo command: `env -i PATH="$PATH" HOME="$HOME" LANG=C.UTF-8`, plus only the command's own variables. The proxy and CA variables pass by reference, never printed (`docs/operations/local-development.md`).

## 2. Start gate

```bash
git fetch origin claude/magical-wozniak-yfmmx2 main
git switch -C <your session branch> <START_SHA>   # your branch starts at this prompt's commit
git rev-parse HEAD                                  # must print <START_SHA>
git merge-base --is-ancestor <START_SHA> origin/claude/magical-wozniak-yfmmx2 && echo "this prompt's commit is on the live branch"
git diff --quiet 0881db514b96dd6b35ae54f8759af68dee20e3d7 HEAD -- .github scripts services apps packages proofs && echo "the code head under correction"
git diff --quiet 0881db514b96dd6b35ae54f8759af68dee20e3d7 origin/claude/magical-wozniak-yfmmx2 -- .github scripts services apps packages proofs && echo "no code on the live branch after 0881db5"
git show origin/claude/magical-wozniak-yfmmx2:docs/testing/evidence/2026-11-01-p06-2-f-mobile-hardening.md | grep -c -E '^#+ Correction C2'   # must print 0
```

If a check fails, stop and report. The prompt is stale if its commit is not on the live branch, if a non-Markdown path changed there after `0881db5`, or if the record already holds "Correction C2".

**Then read, completely:**
- root `AGENTS.md` and `CLAUDE.md`; `apps/mobile/AGENTS.md` and `apps/mobile/CLAUDE.md`;
- the brief, whole, with "Correction C1" and "Correction C2" above all;
- the record's "Correction C1", "Manager verification of correction C1" and "Delta re-review of correction C1";
- DM-38's report, whole (`docs/continuity/dev-manager/reviews/2026-11-02-dm-38-p06-2-f-render-rule-check.md`);
- ADR 0003 (`docs/adr/0003-chat-display-rule.md`);
- `src/chat/display-rule.test.ts`, `src/chat/screen.tsx` and `src/chat/rows.ts`, whole.

## 3. What to do

1. **The brief's Outcome 1 to 5,** each with its planted forms added to the test's planted list, each naming the violation the check must report. The 22 planted forms there today must still fail for their named reasons, and today's `screen.tsx` and `rows.ts` must still pass both checks. Keep every existing check.
2. **Each new planted form is a reversal.** Run each also as an edit to `screen.tsx` (or `rows.ts`) in a scratch copy of `apps/mobile` outside the checkout. The test must fail with the edit in place and pass once it is undone. Record each edit and its failing output, and the file's hash after each restore.
3. **Forms of your own,** at least two per mechanism the guarantee names, each recorded with its result: caught, or inside a named limit (say which), or outside every limit. Report a form outside every limit as a finding of your own. Do not widen the guarantee's wording to cover it.
4. **Outcome 6, the guarantee:** the test comment states DM-38 section 4's guarantee word for word, names finding 1's class as a limit an ordinary refactor reaches, and records the `FlatList` false positive (DM-38's F0) with its failing output.
5. **The local checks,** in `apps/mobile`: `npm ci --ignore-scripts`, then `npm run check` (typecheck, lint, every unit test). Record the test count; it must be at least 650.
6. **Push the code commit first,** with `git push -u origin <branch>`, and read its Foundation push run with your GitHub tools: every job's conclusion, the gate's line (`Application checks passed`), the Mobile job's unit-test count (the `@glow/mobile` check's line, not `@glow/contracts`'), the rendered suite's count, and the Mobile job's duration against its 25 minutes. **Push nothing else until that run has completed** (AM8-20): a newer push cancels the run in progress. If the gate's line is not `Application checks passed`, stop and report.
7. **Then the record** (Outcome 7):
   - correct nit 8 in "Correction C1"'s Mobile row, marked "[Corrected in C2: …]" with the old wording;
   - add "Correction C2" after "Delta re-review of correction C1". It holds:
     - the start gate's results, the environment check (names only) and the toolchain versions;
     - the change, and the guarantee as the test states it;
     - each planted form and reversal, with its failing output;
     - your own forms, each with its result and the limit it falls in;
     - every command with its result line;
     - the run of record: its ID, each job, the gate's line, the unit and rendered counts, and Mobile's duration;
     - what you could not run.
   - Commit and push it.

Commit each logical step with a clear message ending in the session's attribution lines. Confirm that `git status` is clean, and that `git diff --name-only <START_SHA> HEAD` lists only the two paths.

## 4. Report

Your final message is the report Nathan relays:
- the prompt revision (revision 1, from `<START_SHA>`), your branch, your code head and your records head;
- the start gate's and the environment check's results;
- for each of Outcome 1 to 5, the mechanism, its planted forms and their reversals, each with its result;
- your own forms, each with its result and the limit it falls in, and any form outside every limit;
- the guarantee as the test states it;
- `npm run check`'s result and test count, and the run of record: its ID, every job, the gate's line, the unit and rendered counts and the Mobile job's duration;
- the record's correction (nit 8);
- anything that met the stop rule, and what you could not run.
