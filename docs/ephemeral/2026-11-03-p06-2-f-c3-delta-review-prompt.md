# P06.2-F correction C3 delta re-review prompt — what the render-rule check does, as a positive list

- **Owner:** App Manager 9. Nathan starts this session manually, in the `Glow App - No Stream` environment (OD-36), and relays its report.
- **Revision 1, 3 November 2026. Revision 2, 3 November 2026:** the start gate compares non-Markdown paths only (`':(exclude)*.md'`), since OD-57's notes changed two Markdown files under `apps/` after `f87e8b1`; nothing else changed.
- **Durable brief:** [P06.2-F — Mobile hardening and P06.2's carried follow-ups](../planning/p06-2-f-mobile-hardening.md), revision 3, "Correction C3", its "Review" line. A delta re-review (manager workflow, step 6): C3 changes no non-test line. It is held to [DM-39](../continuity/dev-manager/reviews/2026-11-02-dm-39-p06-2-f-render-rule-after-c2.md) 1.2.
- **Where the result goes:** the report Nathan relays. The manager records it in the P06.2-F record, "Delta re-review of correction C3", with a disposition for each finding, and in the brief's "Sessions".
- **Model and reasoning setting** (OD-10, OD-30, OD-33, OD-34, OD-42). The reading is the recommendation; it gates nothing, and Nathan picks.
  - **TypeSafe v8.2: Opus 5.5 at high.** Effort score 1.68 (confidence 0.65); rung probabilities low 0.02, medium 0.39, high 0.49, extra high 0.10, max 0.00, ultracode 0.00. Model probabilities Fable 5.1 0.00, Opus 5.5 1.00, Sonnet 5.5 0.00, Haiku 5.5 0.00 (confidence 1.00). Twenty-four cells, computed from the two answers: Fable 5.1 at low 0.000, Fable 5.1 at medium 0.000, Fable 5.1 at high 0.000, Fable 5.1 at extra high 0.000, Fable 5.1 at max 0.000, Fable 5.1 at ultracode 0.000, Opus 5.5 at low 0.020, Opus 5.5 at medium 0.390, Opus 5.5 at high 0.490, Opus 5.5 at extra high 0.100, Opus 5.5 at max 0.000, Opus 5.5 at ultracode 0.000, Sonnet 5.5 at low 0.000, Sonnet 5.5 at medium 0.000, Sonnet 5.5 at high 0.000, Sonnet 5.5 at extra high 0.000, Sonnet 5.5 at max 0.000, Sonnet 5.5 at ultracode 0.000, Haiku 5.5 at low 0.000, Haiku 5.5 at medium 0.000, Haiku 5.5 at high 0.000, Haiku 5.5 at extra high 0.000, Haiku 5.5 at max 0.000, Haiku 5.5 at ultracode 0.000. Flags: boundary between medium and high. Sent 2026-11-03T00:54:53Z. Nathan picks the cell.
- **The Dev Manager's read:** none before it runs. The review authorizes no credential use and no live provider action.
- **Environment** (OD-36): `Glow App - No Stream`. No Stream variable is needed.
- **It runs alone** (OD-29), after Codex's review of PR40's head, which holds this prompt and C3's code (manager workflow, step 6).
- **Deletion condition:** prune after PR40 merges and its merge receipt is recorded.

**Manager:** before giving this prompt to Nathan, replace every `<PROMPT_SHA>` with the full SHA of the manager-branch commit that holds this revision.

---

You are the **delta re-review of correction C3 of P06.2-F**, the mobile hardening, for the Glow dating app, in the public repository `amthorn78/glow-dating-app` (public for now; OD-51). You review one correction at one exact code head. This prompt is revision 2, from commit `<PROMPT_SHA>` of the manager branch `claude/magical-wozniak-yfmmx2`.

**What came before.**
- **The render-rule test** (`apps/mobile/src/chat/display-rule.test.ts`) checks from source that `src/chat/screen.tsx` and `src/chat/rows.ts` render only contract fields, never a provider-shaped one (ADR 0003). It has two parts: a source check, which is a text match, and a type check built on the TypeScript compiler. Corrections C1 and C2 built the type check and its planted forms.
- **Three rounds found forms the check's stated claim did not cover:** P06.2-F's exact-head review, C1's delta re-review, and C2's own probes. C2's probes found 49 forms in nine classes, N1 to N9, among them N1's X2, an ordinary refactor. Codex found N1 and N8 again (`display-rule.test.ts:280` and `:415`).
- **The Dev Manager's DM-39** kept the checks as they are and changed the claim. The test comment and the record now say what the check refuses, as a positive list, and name what it is known to pass. DM-38 section 4's wording is withdrawn. The structural fix is view models built by explicit field copy, carried to a later change, before P11 at the latest.
- **Correction C3** (branch `ccr-7506019b-5rfdfn`, code head `f87e8b1`, records `14e37a6`; the record's "Correction C3"):
  - it replaces the test comment's guarantee with DM-39 section 4.2's core paragraph, word for word, followed by three lists: what the check refuses, with the planted forms that pin each item; what it is known to pass; and what harmless code it refuses;
  - it marks the refusals that no planted form pins and confirms each by a probe, adding no planted form (DM-39 1.1);
  - it notes four forms that the source check passes as a text match and the type check refuses;
  - it records that C2's per-class counts sum to 48, not 49;
  - no check, exception or planted form changed.
- **Its run of record,** push run 41553218994 on `f87e8b1`:
  - all eight jobs passed, and the gate printed `Application checks passed`;
  - 650 of 650 unit tests, and the rendered suite `97 passed (5.0m)`;
  - Mobile took 7 min 42 s of its 25.
- **The manager verified it** (the record, "Manager verification of correction C3"). Both versions of the test, printed from their parse trees with comments removed, are identical. The core paragraph matches word for word. The coverage words appear only as the type `any`, the method `every`, the mandated "any other form", and limits ("does not follow"). The run's jobs and lines were read. The manager then integrated it by a merge commit.

**The code head under review is `f87e8b1`.** You work at `<PROMPT_SHA>`, whose non-Markdown paths are byte-identical to `f87e8b1` (the start gate checks this). Two Markdown files under `apps/mobile/` changed after it, for Nathan's OD-57 (`AGENTS.md` and `README.md`: Playwright in a CLI environment). They are governing or ordinary documentation for the Dev Manager's read, not under this review.

**Your scope (a delta review: every path C3 touches, read whole as it stands at the head, not the diff alone):**
- **The test file:** `apps/mobile/src/chat/display-rule.test.ts`, whole. Use `git diff 816cd607019e69442f99007ef6324c9aa00dd83c f87e8b19110544b1ceddfc1afd44a8492350fb81` as the guide to what changed.
- **The P06.2-F record,** `docs/testing/evidence/2026-11-01-p06-2-f-mobile-hardening.md`: its "Correction C3" and "Manager verification of correction C3", checked against the code and the runs. Its "Correction C2" is the source for N1 to N9 and the false positives.
- **Read as context, not under review:** `src/chat/screen.tsx` and `src/chat/rows.ts` (the files the check reads), and each file in the test's `GLOW_DATA` list.
- **The runs:** run 41553218994, and the PR run on PR40's final head (event `pull_request`) once it has finished.
- **Out of scope:** code that C3 does not change. A finding about the check's behaviour that C3's comment states truly is a records line under DM-39 1.2, not a defect of C3.

**The standard (DM-39 1.2):**
- a form that evades a listed refusal is a finding;
- a form outside the list that passes is recorded as a known passing class (a records line), not a finding;
- you try forms of your own against each listed refusal.

**The focus (the review's security focus is the display rule: no provider-shaped field reaches member-visible output):**
1. **Only comments changed** (DM-39 1.1). No refusal, exception, planted form or other code line changed from `816cd60`. Show it your own way, for example by comparing both files printed from their parse trees without comments, or their emitted JavaScript.
2. **The core paragraph** stands word for word as the brief's "Correction C3" gives it, in the comment and in the record.
3. **Each listed refusal holds.** Try forms of your own against each item of "What it refuses, in its own terms", as real edits to `screen.tsx` or `rows.ts` in a scratch copy. Include the items whose bracket says no planted form pins them (a rest read; an `in` check, a `for…in` or a destructuring assignment of Glow's data; a widening through `bind`, a return or an assignment, or to `object` or `{}`; an inferred predicate; a type error; `any` and an `in` check on a string in the source check). A form that evades a listed refusal is a finding.
4. **The brackets are true.** Each planted form an item cites fails for that item's reason, under the comment's rule for the source-check items (a form pins one only when that item is its only source-check violation). Each "no planted form" bracket is also true.
5. **The known-passing list is true.** Each class's example passes as written, at least one per class, and each is described faithfully from the record's "Correction C2". An example that the check in fact refuses is a records finding.
6. **The harmless-code list is true,** with the stated reasons. The reason given for `Iterable` in F0's family is one that C3's verifiers corrected; check it.
7. **No words that claim coverage of code paths** (DM-38 4.2): no "follows", "any", "every", "all" or "wherever" about what the check covers, in the comment or the record.
8. **The records:** every claim in "Correction C3" and "Manager verification of correction C3" holds against the code and the runs, and claims no more than they show. That includes the four source-check misses, the 48-or-49 count and what it says was not re-run.
9. **The planted-form specification.** The core paragraph says the planted forms are the list's specification, and the comment marks the refusals that no planted form pins. Say whether that is stated truly. Then give your view: should those refusals get planted forms before the merge, or should they stay as marked, given that option (c) replaces this check (DM-39 4.1)? Say whether it falls in a correction class. The manager disposes of it, and takes it to the Dev Manager if planting forms would depart from DM-39 1.1.

**What comes after this review: the correction classes.** Report every finding with its severity. Another correction pass takes every blocking finding, and any should-fix finding that could do any of these:
- let a form evade a refusal the comment lists (DM-39 1.2);
- change a line of the test other than a comment, or weaken what any test proves;
- make the test pass vacuously;
- add a dependency, change a lock, or change runtime code;
- make the comment or a record claim more than the code, the tests or the runs show. That includes a wrong planted-form ID, a false "no planted form" bracket, a known-passing example the check refuses, and a word that claims coverage of code paths.

A passing form outside the list is a records line, not a finding (DM-39 1.2). Everything else goes into the records. For each finding, say whether it falls in one of these classes.

**How you work:**
- Nathan started you and will relay your report to the manager, App Manager 9. You are neither the manager nor an implementer.
- You may use any tools, subagents, scheduled wake-ups or other capabilities the review needs, including Claude Code's code-review and security-review capabilities.
- Your boundary is scope: review one exact head and report.
  - **Change nothing** in the repository, on GitHub or in Notion: no commits, pushes, PR comments, re-runs or workflow dispatches.
  - **Scratch work goes in a copy outside the repository,** never the checkout (DM-14 item 6). Use absolute paths, and confirm afterwards that `git status` is clean.
- **Network:** the npm registry only, for `npm ci --ignore-scripts` in a scratch copy.
- **Rendered tests:** C3 changes no rendered path; CI's run is the evidence. Never run `playwright install`.
- **Never:**
  - dump the environment, or print a credential, token or password;
  - call Stream or any other provider, or run any command in `proofs/stream-chat/`;
  - connect to any database, HDE, Railway or other external service;
  - run `playwright install`, `eas` or `migrate`, or a package install script.

## 1. Environment check (names only; never print values)

1. None of `DATABASE_URL`, `HD_API_KEY` or `GEO_API_KEY` may be set: `for n in DATABASE_URL HD_API_KEY GEO_API_KEY; do [ -n "${!n+x}" ] && echo "$n present"; done`. If any is present, stop and report.
2. **No `STREAM_*` name may be set:** `compgen -e | grep -E '^STREAM_'` prints names only. If any is present, stop and report: this session must start in `Glow App - No Stream`.
3. **GitHub token names** may be present (`GITHUB_TOKEN`, `GH_TOKEN`). Never read them; every command below runs without them.
4. **The toolchain:** Node 24.19.0 and npm 11.9.0 in `$HOME/.local/bin`, first on PATH (C3 found another directory before it on its PATH, so put it first yourself). Record their versions.
5. **A clean process environment** for every repository command: `env -i PATH="$HOME/.local/bin:$PATH" HOME="$HOME" LANG=C.UTF-8`, plus only the command's own variables.

## 2. Start gate

```bash
git fetch origin claude/magical-wozniak-yfmmx2 main
git switch --detach <PROMPT_SHA>
git rev-parse HEAD                                    # must print <PROMPT_SHA>
git merge-base --all origin/main HEAD                 # expected: one line, 05f4c3a0f78e72a5782fef62db4ef186a8558ac3
git merge-base --is-ancestor <PROMPT_SHA> origin/claude/magical-wozniak-yfmmx2 && echo "this prompt's commit is on the live branch"
git diff --quiet f87e8b19110544b1ceddfc1afd44a8492350fb81 HEAD -- .github scripts services apps packages proofs ':(exclude)*.md' && echo "the code head under review"
git diff --quiet f87e8b19110544b1ceddfc1afd44a8492350fb81 origin/claude/magical-wozniak-yfmmx2 -- .github scripts services apps packages proofs ':(exclude)*.md' && echo "no code on the live branch after f87e8b1"
git show origin/claude/magical-wozniak-yfmmx2:docs/testing/evidence/2026-11-01-p06-2-f-mobile-hardening.md | grep -c -E '^#+ Delta re-review of correction C3'   # must print 0
```

If any check fails, stop and report. The prompt is stale if its commit is not on the live branch, if a non-Markdown path changed there after `f87e8b1`, or if this review is already recorded.

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
- the brief, with "Correction C2" and "Correction C3";
- the P06.2-F record's "Correction C1", "Correction C2", "Manager verification of correction C2", "Correction C3" and "Manager verification of correction C3";
- DM-39's report, whole;
- ADR 0003 (`docs/adr/0003-chat-display-rule.md`);
- `src/chat/display-rule.test.ts`, `src/chat/screen.tsx` and `src/chat/rows.ts`, whole.

**The runs,** with your GitHub tools:
- **run 41553218994:** every job's conclusion, the gate's line, and the Mobile job's unit-test count, rendered result and duration;
- **the PR run on PR40's final head,** if it has finished.

## 3. What to do

1. Review against the focus, item by item.
2. **In a scratch copy of `f87e8b1`:**
   - in `apps/mobile`, run `npm ci --ignore-scripts`, then `npm run check`, then `node --test src/chat/display-rule.test.ts`;
   - try forms of your own against each listed refusal, each as an edit to `screen.tsx` or `rows.ts`, with the result before and after;
   - check the cited planted forms and the known-passing examples you sample.
3. For each finding: its severity (blocking, should fix, nit), its file and line, the evidence, and whether it falls in a correction class.

## 4. Report

Your final message is the report Nathan relays:
- the prompt revision (revision 2, from `<PROMPT_SHA>`), and the start gate's, the classification's and the environment check's results;
- **the verdict:** approve, approve with nits, or changes required;
- **the findings,** in a table: number, severity, correction class or not, file and line, what is wrong, and the evidence;
- **the passing forms you found outside the list,** as records lines, each with its class;
- **the answer to each focus point (1 to 9),** one or two lines each, with focus 9's view;
- **the forms you tried,** each with its result;
- **what you ran,** and what you could not run or read.
