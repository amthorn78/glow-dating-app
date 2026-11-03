# P06.2-F correction C1 delta re-review prompt — the render-rule type check and the copy test's word list

- **Owner:** App Manager 9. Nathan starts this session manually, in the `Glow App - No Stream` environment (OD-36), and relays its report.
- **Revision 1, 2 November 2026.**
- **Durable brief:** [P06.2-F — Mobile hardening and P06.2's carried follow-ups](../planning/p06-2-f-mobile-hardening.md), revision 1, "Correction C1", its "Review" line. A delta re-review on M05 S2's terms (OD-53; manager workflow, step 6): C1 changes no non-test line.
- **Where the result goes:** the report Nathan relays. The manager records it in the P06.2-F record, "Delta re-review of correction C1", with a disposition for each finding, and in the brief's "Sessions".
- **Model and reasoning setting** (OD-10, OD-30, OD-33, OD-34, OD-42). The reading is the recommendation; it gates nothing, and Nathan picks.
  - **TypeSafe v8.2: Opus 5.5 at high.** Effort score 2.08 (confidence 0.81); rung probabilities low 0.00, medium 0.11, high 0.71, extra high 0.18, max 0.00, ultracode 0.00. Model probabilities Fable 5.1 0.00, Opus 5.5 1.00, Sonnet 5.5 0.00, Haiku 5.5 0.00 (confidence 1.00). Twenty-four cells, computed from the two answers: Fable 5.1 at low 0.000, Fable 5.1 at medium 0.000, Fable 5.1 at high 0.000, Fable 5.1 at extra high 0.000, Fable 5.1 at max 0.000, Fable 5.1 at ultracode 0.000, Opus 5.5 at low 0.000, Opus 5.5 at medium 0.110, Opus 5.5 at high 0.710, Opus 5.5 at extra high 0.180, Opus 5.5 at max 0.000, Opus 5.5 at ultracode 0.000, Sonnet 5.5 at low 0.000, Sonnet 5.5 at medium 0.000, Sonnet 5.5 at high 0.000, Sonnet 5.5 at extra high 0.000, Sonnet 5.5 at max 0.000, Sonnet 5.5 at ultracode 0.000, Haiku 5.5 at low 0.000, Haiku 5.5 at medium 0.000, Haiku 5.5 at high 0.000, Haiku 5.5 at extra high 0.000, Haiku 5.5 at max 0.000, Haiku 5.5 at ultracode 0.000. Sent 2026-11-02T12:30:24Z. Nathan picks the cell.
- **The Dev Manager's read:** none before it runs. The review authorizes no credential use and no live provider action.
- **Environment** (OD-36): `Glow App - No Stream`. No Stream variable is needed.
- **It runs alone** (OD-29), after Codex's review of PR40's head, which holds this prompt (manager workflow, step 6).
- **Deletion condition:** prune after PR40 merges and its merge receipt is recorded.

**Manager:** before giving this prompt to Nathan, replace every `<PROMPT_SHA>` with the full SHA of the manager-branch commit that holds this revision.

---

You are the **delta re-review of correction C1 of P06.2-F**, the mobile hardening, for the Glow dating app, in the public repository `amthorn78/glow-dating-app` (public for now; OD-51). You review one correction at one exact code head. This prompt is revision 1, from commit `<PROMPT_SHA>` of the manager branch `claude/magical-wozniak-yfmmx2`.

**What came before.**
- **P06.2-F** (code head `3db50d8`) closed seven fixture-only items in `apps/mobile`, each with a test and its reversal. Its exact-head review asked for changes in one test and the record; the runtime code is correct, no guard allows anything new and no test is weakened (the record, "Exact-head review of P06.2-F").
- **Finding 1 (should fix):** the render-rule check in `src/chat/display-rule.test.ts` read only the paths reached through six variable names, so a renamed binding (PA) or a loosely typed helper prop (PB) rendered a provider-shaped field and passed. Codex raised the same probe on `cdc7c48` (its thread at `display-rule.test.ts:133`). **Finding 2 (nit):** the copy test's word list lacked plurals, `cloudflare` and `allauth`. **Findings 5, 6, 8 and 10:** nits in the record.
- **Correction C1** (branch `claude/trusting-cori-gxlila`, code head `0881db5`, records `0e98f25`; the record's "Correction C1"): the source check is kept, with an `in` check on a string literal added; beside it, a **type check** built on the installed TypeScript compiler finds Glow's data by type through any binding and refuses reads of undeclared fields, widenings, spreads, enumerations, local generics and overloads, with four named exceptions; 22 planted forms (the nine old ones, PA, PB, PC and ten of the session's own) each must fail it for a named reason. The word list is widened. The record's corrections are marked "[Corrected in C1: …]".
- **Its run of record,** push run 41383619096 on `0881db5`: all eight jobs passed, the gate printed `Application checks passed`, 650 of 650 unit tests, the rendered suite `97 passed (5.0m)`, Mobile 7 min 27 s of 25.
- **The manager verified it** (the record, "Manager verification of correction C1"): 650 of 650 locally; PA, PB, PC and finding 2's reversal re-run as real edits, each failing and passing once undone; the other-module evasion the record names confirmed; then integrated into the manager branch by a merge commit.

**The code head under review is `0881db5`.** You work at `<PROMPT_SHA>`, whose non-Markdown paths are byte-identical to `0881db5` (the start gate checks this).

**Your scope (a delta review: every path C1 touches, read whole as it stands at the head, not the diff alone):**
- `apps/mobile/src/chat/display-rule.test.ts`, whole, with `git diff cdc7c487d26fe31c19878b6079750f9c5a42d59c 0881db514b96dd6b35ae54f8759af68dee20e3d7` as the guide to what changed;
- the P06.2-F record, `docs/testing/evidence/2026-11-01-p06-2-f-mobile-hardening.md`: the C1 corrections in the session's sections, "Correction C1" and "Manager verification of correction C1", against the code and the runs;
- **read as context, not under review:** `src/chat/screen.tsx` and `src/chat/rows.ts` (the files the check reads), and each file in the test's `GLOW_DATA` list;
- **the runs:** run 41383619096, and the PR run on PR40's final head (event `pull_request`) once it has finished.
- **Out of scope:** code C1 does not change, and the parts of P06.2-F the exact-head review already passed. A finding there is reported as pre-existing.

**The focus (the review's security focus is the display rule: no provider-shaped field reaches member-visible output):**
1. **The type check closes finding 1.** Does it refuse a provider-shaped field rendered through any binding inside `screen.tsx` and `rows.ts`, PA, PB and PC included, for the reason each planted form names, and not only through a type error? Try forms of your own in a scratch copy.
2. **The named exceptions allow only what they say.** The value an Array predicate returns; an element of a React hook's dependency list; the initializer of an unannotated object destructuring; a type parameter declared outside the two files. Can any exception carry a provider-shaped field to output, or hide a widening?
3. **No vacuous pass.** Could the test pass while checking nothing: a wrong `GLOW_DATA` path, a type of Glow's data declared in a file the list omits, the program failing to load a file, a planted path that does not resolve? Does the planted-forms test, with its named violations, catch each such failure?
4. **No earlier check is weakened.** The source check is kept whole; the nine original forms still fail it (now placed in the screen, not appended to the source); the copy-table test and the `invalid_response` assertions are unchanged in strength; nothing removed or loosened.
5. **No harmless code fails, and the coupling is acceptable.** Today's two files pass both checks unchanged. The planted forms are anchored on exact lines of `screen.tsx`, so an edit to those lines fails the planted test until its anchors move; say whether that fails closed and whether it is acceptable.
6. **Finding 2.** The widened word list covers `src/components/provider-wording.test.ts`'s terms with plurals, and makes no member-visible string in `copy.ts` fail by accident.
7. **No dependency, lock, runtime or bundle change.** `typescript` is imported only by the test, already a devDependency; nothing it imports reaches the app's bundle.
8. **The records:** every C1 claim, the known evasions above all (a module outside the two files; a template literal's coercion), holds against the code and the runs, and claims no more than they show.

**What comes after this review: the correction classes.** Report every finding with its severity. Another correction pass takes every blocking finding, and any should-fix finding that could do any of these:
- let the render-rule test pass where it should fail, or weaken what any test proves;
- let a provider-shaped field reach member-visible output in `screen.tsx` or `rows.ts` without failing the test, other than through the evasions the record names;
- make the test pass vacuously;
- add a dependency, change a lock, or change runtime code;
- make a record claim more than the code, the tests or the runs show.

Everything else goes into the records. For each finding, say whether it falls in one of these classes.

**How you work:**
- Nathan started you and will relay your report to the manager, App Manager 9. You are neither the manager nor an implementer.
- You may use any tools, subagents, scheduled wake-ups or other capabilities the review needs, including Claude Code's code-review and security-review capabilities.
- Your boundary is scope: review one exact head and report.
  - **Change nothing** in the repository, on GitHub or in Notion: no commits, pushes, PR comments, re-runs or workflow dispatches.
  - **Scratch work goes in a copy outside the repository,** never the checkout (DM-14 item 6). Use absolute paths, and confirm afterwards that `git status` is clean.
- **Network:** the npm registry only, for `npm ci --ignore-scripts` in a scratch copy.
- **Rendered tests:** C1 changes no rendered path; CI's run is the evidence. Never run `playwright install`.
- **Never:**
  - dump the environment, or print a credential, token or password;
  - call Stream or any other provider, or run any command in `proofs/stream-chat/`;
  - connect to any database, HDE, Railway or other external service;
  - run `playwright install`, `eas` or `migrate`, or a package install script.

## 1. Environment check (names only; never print values)

1. None of `DATABASE_URL`, `HD_API_KEY` or `GEO_API_KEY` may be set: `for n in DATABASE_URL HD_API_KEY GEO_API_KEY; do [ -n "${!n+x}" ] && echo "$n present"; done`. If any is present, stop and report.
2. **No `STREAM_*` name may be set:** `compgen -e | grep -E '^STREAM_'` prints names only. If any is present, stop and report: this session must start in `Glow App - No Stream`.
3. **GitHub token names** may be present (`GITHUB_TOKEN`, `GH_TOKEN`). Never read them; every command below runs without them.
4. **The toolchain:** Node 24.19.0 and npm 11.9.0 in `$HOME/.local/bin`, first on PATH. Record their versions.
5. **A clean process environment** for every repository command: `env -i PATH="$PATH" HOME="$HOME" LANG=C.UTF-8`, plus only the command's own variables.

## 2. Start gate

```bash
git fetch origin claude/magical-wozniak-yfmmx2 main
git switch --detach <PROMPT_SHA>
git rev-parse HEAD                                    # must print <PROMPT_SHA>
git merge-base --all origin/main HEAD                 # expected: one line, 05f4c3a0f78e72a5782fef62db4ef186a8558ac3
git merge-base --is-ancestor <PROMPT_SHA> origin/claude/magical-wozniak-yfmmx2 && echo "this prompt's commit is on the live branch"
git diff --quiet 0881db514b96dd6b35ae54f8759af68dee20e3d7 HEAD -- .github scripts services apps packages proofs && echo "the code head under review"
git diff --quiet 0881db514b96dd6b35ae54f8759af68dee20e3d7 origin/claude/magical-wozniak-yfmmx2 -- .github scripts services apps packages proofs && echo "no code on the live branch after 0881db5"
git show origin/claude/magical-wozniak-yfmmx2:docs/testing/evidence/2026-11-01-p06-2-f-mobile-hardening.md | grep -c -E '^#+ Delta re-review of correction C1'   # must print 0
```

If any check fails, stop and report. The prompt is stale if its commit is not on the live branch, if a non-Markdown path changed there after `0881db5`, or if this review is already recorded.

**Classify the change** as root `AGENTS.md` requires, with the trusted base policy outside the candidate tree:

```bash
base=$(git rev-parse origin/main); head=$(git rev-parse HEAD)
policy_dir=$(mktemp -d)
git show "$base:scripts/change_scope.py" > "$policy_dir/change_scope.py"
python3 -I "$policy_dir/change_scope.py" --base "$base" --head "$head" --merge-base
```

Expected: `"full": true`. Anything else: stop and report.

**Then read, completely, at `HEAD`:**
- root `AGENTS.md` and `CLAUDE.md`; `apps/mobile/AGENTS.md`;
- the brief, with "Correction C1";
- the P06.2-F record, whole, with "Exact-head review of P06.2-F", "Correction C1" and "Manager verification of correction C1";
- ADR 0003 (`docs/adr/0003-chat-display-rule.md`);
- `src/chat/display-rule.test.ts`, `src/chat/screen.tsx` and `src/chat/rows.ts`, whole.

**The runs,** with your GitHub tools:
- run 41383619096: every job's conclusion, the gate's line, the Mobile job's unit-test count, rendered result and duration;
- the PR run on PR40's final head, if it has finished.

## 3. What to do

1. Review against the focus, item by item.
2. In a scratch copy of `0881db5`: `npm ci --ignore-scripts` and `npm run check` in `apps/mobile`; then try forms of your own against the type check, and any reversal you doubt, each as an edit to `screen.tsx` or `rows.ts` with the result before and after.
3. For each finding: its severity (blocking, should fix, nit), its file and line, the evidence, and whether it falls in a correction class.

## 4. Report

Your final message is the report Nathan relays:
- the prompt revision (revision 1, from `<PROMPT_SHA>`), and the start gate's, the classification's and the environment check's results;
- **the verdict:** approve, approve with nits, or changes required;
- the findings, in a table: number, severity, correction class or not, file and line, what is wrong, and the evidence;
- the answer to each focus point (1 to 8), one or two lines each;
- the forms you tried, each with its result;
- what you ran, and what you could not run or read.
